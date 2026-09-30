"""Roteadores FastAPI para o Módulo Comercial / Vendas."""

from typing import List, Optional
from datetime import datetime
import uuid
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db_session
from src.core.models import SalesOrderORM, SalesOrderItemORM

router = APIRouter(prefix="/api/v1/sales", tags=["Comercial & Vendas"])


class SalesOrderItemInput(BaseModel):
    product_sku: str
    product_name: str
    quantity: int = Field(default=1, ge=1)
    unit_price: float = Field(default=0.0, ge=0)


class SalesOrderCreateDTO(BaseModel):
    customer_name: str
    representative_name: Optional[str] = "Vendas Diretas"
    items: List[SalesOrderItemInput]


class SalesOrderResponseDTO(BaseModel):
    id: int
    order_number: str
    customer_name: str
    representative_name: str
    total_amount: float
    status: str
    created_at: Optional[datetime] = None


@router.post("", response_model=SalesOrderResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_sales_order(
    dto: SalesOrderCreateDTO,
    session: AsyncSession = Depends(get_db_session)
):
    if not dto.items:
        raise HTTPException(status_code=400, detail="O pedido de venda deve conter ao menos um item.")

    ord_num = f"VEN-{datetime.utcnow().year}-{uuid.uuid4().hex[:4].upper()}"
    total = sum(it.quantity * it.unit_price for it in dto.items)

    order = SalesOrderORM(
        order_number=ord_num,
        customer_name=dto.customer_name,
        representative_name=dto.representative_name or "Vendas Diretas",
        total_amount=total,
        status="Confirmado"
    )
    session.add(order)
    await session.flush()

    for it in dto.items:
        it_orm = SalesOrderItemORM(
            order_id=order.id,
            product_sku=it.product_sku,
            product_name=it.product_name,
            quantity=it.quantity,
            unit_price=it.unit_price,
            total_price=it.quantity * it.unit_price
        )
        session.add(it_orm)

    await session.commit()
    await session.refresh(order)
    return SalesOrderResponseDTO(
        id=order.id,
        order_number=order.order_number,
        customer_name=order.customer_name,
        representative_name=order.representative_name,
        total_amount=order.total_amount,
        status=order.status,
        created_at=order.created_at
    )


@router.get("", response_model=List[SalesOrderResponseDTO])
async def list_sales_orders(session: AsyncSession = Depends(get_db_session)):
    stmt = select(SalesOrderORM).order_by(SalesOrderORM.id.desc())
    res = await session.execute(stmt)
    orders = res.scalars().all()

    if not orders:
        seed = [
            SalesOrderORM(order_number="VEN-2026-0081", customer_name="Cliente Atlântico Ltda", total_amount=78200.0, status="Em separação"),
            SalesOrderORM(order_number="VEN-2026-0080", customer_name="Distribuidora Sul", total_amount=43150.0, status="Expedido")
        ]
        for it in seed:
            session.add(it)
        await session.commit()
        stmt = select(SalesOrderORM).order_by(SalesOrderORM.id.desc())
        res = await session.execute(stmt)
        orders = res.scalars().all()

    return [
        SalesOrderResponseDTO(
            id=o.id,
            order_number=o.order_number,
            customer_name=o.customer_name,
            representative_name=o.representative_name or "Vendas Diretas",
            total_amount=o.total_amount,
            status=o.status,
            created_at=o.created_at
        )
        for o in orders
    ]
