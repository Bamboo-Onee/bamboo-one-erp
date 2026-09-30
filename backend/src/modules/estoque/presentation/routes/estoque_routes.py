"""Roteadores FastAPI para o Módulo de Estoque e Movimentações."""

from typing import List, Optional
from datetime import datetime
import uuid
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db_session
from src.core.models import StockBalanceORM, StockMovementORM

router = APIRouter(prefix="/api/v1/stock", tags=["Estoque"])


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
    session: AsyncSession = Depends(get_db_session)
):
    mov_num = f"MOV-{uuid.uuid4().hex[:6].upper()}"
    mov = StockMovementORM(
        movement_number=mov_num,
        movement_type=dto.movement_type,
        product_sku=dto.product_sku,
        warehouse_name=dto.warehouse_name,
        quantity=dto.quantity,
        reason=dto.reason,
        user_name=dto.user_name
    )
    session.add(mov)

    # Atualiza ou cria saldo do produto no depósito
    stmt = select(StockBalanceORM).where(
        StockBalanceORM.product_sku == dto.product_sku,
        StockBalanceORM.warehouse_name == dto.warehouse_name
    )
    res = await session.execute(stmt)
    balance = res.scalar_one_or_none()

    delta = dto.quantity if dto.movement_type in ["Entrada", "Ajuste"] else -dto.quantity

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
        balance.quantity_available = max(0, balance.quantity_available + delta)

    await session.commit()
    return {
        "status": "success",
        "movement_number": mov_num,
        "new_quantity_available": balance.quantity_available
    }


@router.get("/balances", response_model=List[StockBalanceDTO])
async def list_stock_balances(session: AsyncSession = Depends(get_db_session)):
    stmt = select(StockBalanceORM).order_by(StockBalanceORM.id.desc())
    res = await session.execute(stmt)
    balances = res.scalars().all()

    # Seed inicial demonstrativo caso vazio
    if not balances:
        initial = [
            StockBalanceORM(product_sku="BAM-0082", product_name="Caixa Master A", warehouse_name="CD Principal", quantity_available=138, quantity_reserved=24),
            StockBalanceORM(product_sku="BAM-0154", product_name="Pallet B", warehouse_name="CD Principal", quantity_available=34, quantity_reserved=8),
            StockBalanceORM(product_sku="BAM-0221", product_name="Volume Frágil", warehouse_name="CD Principal", quantity_available=52, quantity_reserved=12)
        ]
        for it in initial:
            session.add(it)
        await session.commit()
        stmt = select(StockBalanceORM).order_by(StockBalanceORM.id.desc())
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
