"""Roteadores FastAPI para o Módulo de Estoque e Movimentações."""

import asyncio
from typing import List, Optional
from datetime import datetime
import uuid
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db_session
from src.core.models import StockBalanceORM, StockMovementORM, UserORM
from src.modules.auth.presentation.routes.auth_routes import require_roles

router = APIRouter(prefix="/api/v1/stock", tags=["Estoque"])

_stock_lock = asyncio.Lock()
VALID_MOVEMENT_TYPES = {"Entrada", "Saída", "Transferência", "Ajuste"}


class StockMovementCreateDTO(BaseModel):
    movement_type: str = Field(..., description="Entrada, Saída, Transferência, Ajuste")
    product_sku: str
    product_name: str
    warehouse_name: str = "CD Principal"
    quantity: int = Field(..., gt=0)
    reason: str
    user_name: str = "Operador Estoque"


class StockBalanceDTO(BaseModel):
    id: int
    product_sku: str
    product_name: str
    warehouse_name: str
    quantity_available: int
    quantity_reserved: int
    updated_at: Optional[datetime] = None


@router.post("/movements", status_code=status.HTTP_201_CREATED)
async def create_stock_movement(
    dto: StockMovementCreateDTO,
    session: AsyncSession = Depends(get_db_session),
    current_user: UserORM = Depends(require_roles(["LOGISTICA"]))
):
    if dto.movement_type not in VALID_MOVEMENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de movimentação inválido."
        )

    mov_num = f"MOV-{uuid.uuid4().hex[:6].upper()}"
    delta = dto.quantity if dto.movement_type in {"Entrada", "Ajuste"} else -dto.quantity

    async with _stock_lock:
        stmt = (
            select(StockBalanceORM)
            .where(
                StockBalanceORM.product_sku == dto.product_sku,
                StockBalanceORM.warehouse_name == dto.warehouse_name
            )
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        res = await session.execute(stmt)
        balance = res.scalar_one_or_none()

        if dto.movement_type in {"Saída", "Transferência"}:
            if not balance or balance.quantity_available < dto.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Saldo insuficiente em estoque para esta operação."
                )

        if not balance:
            balance = StockBalanceORM(
                product_sku=dto.product_sku,
                product_name=dto.product_name,
                warehouse_name=dto.warehouse_name,
                quantity_available=max(0, delta),
                quantity_reserved=0
            )
            session.add(balance)
        else:
            await session.execute(
                update(StockBalanceORM)
                .where(StockBalanceORM.id == balance.id)
                .values(quantity_available=StockBalanceORM.quantity_available + delta)
            )

        mov = StockMovementORM(
            movement_number=mov_num,
            movement_type=dto.movement_type,
            product_sku=dto.product_sku,
            warehouse_name=dto.warehouse_name,
            quantity=dto.quantity,
            reason=dto.reason,
            user_name=dto.user_name or current_user.name
        )
        session.add(mov)

        await session.commit()
        await session.refresh(balance)

        return {
            "status": "success",
            "movement_number": mov_num,
            "new_quantity_available": balance.quantity_available
        }


@router.get("/balances", response_model=List[StockBalanceDTO])
async def list_stock_balances(
    session: AsyncSession = Depends(get_db_session),
    _: UserORM = Depends(require_roles(["LOGISTICA", "VENDAS", "COMPRAS"]))
):
    stmt = select(StockBalanceORM).order_by(StockBalanceORM.id.desc())
    res = await session.execute(stmt)
    balances = res.scalars().all()

    # Seed inicial demonstrativo caso vazio
    if not balances:
        async with _stock_lock:
            res = await session.execute(stmt)
            balances = res.scalars().all()
            if not balances:
                initial = [
                    StockBalanceORM(product_sku="BAM-0082", product_name="Caixa Master A", warehouse_name="CD Principal", quantity_available=138, quantity_reserved=24),
                    StockBalanceORM(product_sku="BAM-0154", product_name="Pallet B", warehouse_name="CD Principal", quantity_available=34, quantity_reserved=8),
                    StockBalanceORM(product_sku="BAM-0221", product_name="Volume Frágil", warehouse_name="CD Principal", quantity_available=52, quantity_reserved=12)
                ]
                for it in initial:
                    session.add(it)
                try:
                    await session.commit()
                except IntegrityError:
                    await session.rollback()
                res = await session.execute(stmt)
                balances = res.scalars().all()

    return [
        StockBalanceDTO(
            id=b.id,
            product_sku=b.product_sku,
            product_name=b.product_name,
            warehouse_name=b.warehouse_name,
            quantity_available=b.quantity_available,
            quantity_reserved=b.quantity_reserved,
            updated_at=b.updated_at
        )
        for b in balances
    ]
