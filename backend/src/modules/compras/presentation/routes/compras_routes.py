"""Roteadores FastAPI para o Módulo de Compras Nacionais."""

from typing import List, Optional
from datetime import datetime
import uuid
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db_session
from src.core.models import PurchaseOrderORM, PurchaseOrderItemORM

router = APIRouter(prefix="/api/v1/purchases", tags=["Compras Nacionais"])


class PurchaseItemInput(BaseModel):
    product_sku: str
    product_name: str
    quantity: int = Field(default=1, ge=1)
    unit_price: float = Field(default=0.0, ge=0)


class PurchaseOrderCreateDTO(BaseModel):
    supplier_name: str
    items: List[PurchaseItemInput]


class PurchaseOrderResponseDTO(BaseModel):
    id: int
    po_number: str
    supplier_name: str
    total_amount: float
    status: str
    created_at: Optional[datetime] = None


@router.post("", response_model=PurchaseOrderResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_purchase_order(
    dto: PurchaseOrderCreateDTO,
    session: AsyncSession = Depends(get_db_session)
):
    if not dto.items:
        raise HTTPException(status_code=400, detail="O pedido de compra deve conter ao menos um item.")

    po_num = f"PO-{datetime.utcnow().year}-{uuid.uuid4().hex[:4].upper()}"
    total = sum(it.quantity * it.unit_price for it in dto.items)

    po = PurchaseOrderORM(
        po_number=po_num,
        supplier_name=dto.supplier_name,
        total_amount=total,
        status="Enviado"
    )
    session.add(po)
    await session.flush()

    for item in dto.items:
        it_orm = PurchaseOrderItemORM(
            po_id=po.id,
            product_sku=item.product_sku,
            product_name=item.product_name,
            quantity=item.quantity,
            unit_price=item.unit_price,
            total_price=item.quantity * item.unit_price
        )
        session.add(it_orm)

    await session.commit()
    await session.refresh(po)
    return PurchaseOrderResponseDTO(
        id=po.id,
        po_number=po.po_number,
        supplier_name=po.supplier_name,
        total_amount=po.total_amount,
        status=po.status,
        created_at=po.created_at
    )


@router.get("", response_model=List[PurchaseOrderResponseDTO])
async def list_purchase_orders(session: AsyncSession = Depends(get_db_session)):
    stmt = select(PurchaseOrderORM).order_by(PurchaseOrderORM.id.desc())
    res = await session.execute(stmt)
    return [
        PurchaseOrderResponseDTO(
            id=po.id,
            po_number=po.po_number,
            supplier_name=po.supplier_name,
            total_amount=po.total_amount,
            status=po.status,
            created_at=po.created_at
        )
        for po in res.scalars().all()
    ]
