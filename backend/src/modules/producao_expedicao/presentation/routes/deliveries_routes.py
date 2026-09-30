"""Roteadores FastAPI para Produção & Expedição / Entregas."""

from typing import List, Optional
from datetime import datetime
import uuid
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db_session
from src.core.models import DeliveryORM

router = APIRouter(prefix="/api/v1/deliveries", tags=["Produção & Entregas"])


class DeliveryCreateDTO(BaseModel):
    customer_name: str
    destination_city: str
    total_volumes: int = Field(default=1, ge=1)
    vehicle_plate: Optional[str] = "BRA-2E19"
    status: str = "Carga pronta"


class DeliveryResponseDTO(DeliveryCreateDTO):
    id: int
    delivery_number: str
    created_at: Optional[datetime] = None


@router.post("", response_model=DeliveryResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_delivery(
    dto: DeliveryCreateDTO,
    session: AsyncSession = Depends(get_db_session)
):
    del_num = f"ENT-{uuid.uuid4().hex[:5].upper()}"
    deliv = DeliveryORM(
        delivery_number=del_num,
        customer_name=dto.customer_name,
        destination_city=dto.destination_city,
        total_volumes=dto.total_volumes,
        vehicle_plate=dto.vehicle_plate,
        status=dto.status
    )
    session.add(deliv)
    await session.commit()
    await session.refresh(deliv)
    return DeliveryResponseDTO(
        id=deliv.id,
        delivery_number=deliv.delivery_number,
        customer_name=deliv.customer_name,
        destination_city=deliv.destination_city,
        total_volumes=deliv.total_volumes,
        vehicle_plate=deliv.vehicle_plate,
        status=deliv.status,
        created_at=deliv.created_at
    )


@router.get("", response_model=List[DeliveryResponseDTO])
async def list_deliveries(session: AsyncSession = Depends(get_db_session)):
    stmt = select(DeliveryORM).order_by(DeliveryORM.id.desc())
    res = await session.execute(stmt)
    deliveries = res.scalars().all()

    if not deliveries:
        seed = [
            DeliveryORM(delivery_number="ENT-00618", customer_name="Cliente Atlântico Ltda", destination_city="Recife/PE", total_volumes=44, vehicle_plate="BRA-2E19", status="Carga pronta"),
            DeliveryORM(delivery_number="ENT-00617", customer_name="Cliente Horizonte", destination_city="Jaboatão/PE", total_volumes=28, vehicle_plate="PE-9812", status="Em rota")
        ]
        for it in seed:
            session.add(it)
        await session.commit()
        stmt = select(DeliveryORM).order_by(DeliveryORM.id.desc())
        res = await session.execute(stmt)
        deliveries = res.scalars().all()

    return [
        DeliveryResponseDTO(
            id=d.id,
            delivery_number=d.delivery_number,
            customer_name=d.customer_name,
            destination_city=d.destination_city,
            total_volumes=d.total_volumes,
            vehicle_plate=d.vehicle_plate,
            status=d.status,
            created_at=d.created_at
        )
        for d in deliveries
    ]
