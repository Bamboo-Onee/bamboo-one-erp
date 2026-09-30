"""Roteadores FastAPI para o Módulo de Importações Internacionais."""

from typing import List, Optional
from datetime import datetime
import uuid
from pydantic import BaseModel
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db_session
from src.core.models import ImportProcessORM

router = APIRouter(prefix="/api/v1/imports", tags=["Importações"])


class ImportProcessCreateDTO(BaseModel):
    supplier_name: str
    bl_number: Optional[str] = "BL-SH-2026"
    container_number: Optional[str] = "MSCU-821940-1"
    origin_port: str = "Shanghai (CNSHA)"
    destination_port: str = "Santos (BRSSZ)"
    eta: str = "24/09/2026"
    total_usd: float = 28500.0
    landed_cost_brl: float = 162450.0


class ImportProcessResponseDTO(ImportProcessCreateDTO):
    id: int
    process_number: str
    status: str
    created_at: Optional[datetime] = None


@router.post("", response_model=ImportProcessResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_import_process(
    dto: ImportProcessCreateDTO,
    session: AsyncSession = Depends(get_db_session)
):
    proc_num = f"IMP-{datetime.utcnow().year}-{uuid.uuid4().hex[:3].upper()}"
    imp = ImportProcessORM(
        process_number=proc_num,
        supplier_name=dto.supplier_name,
        bl_number=dto.bl_number,
        container_number=dto.container_number,
        origin_port=dto.origin_port,
        destination_port=dto.destination_port,
        status="Em trânsito",
        eta=dto.eta,
        total_usd=dto.total_usd,
        landed_cost_brl=dto.landed_cost_brl
    )
    session.add(imp)
    await session.commit()
    await session.refresh(imp)
    return ImportProcessResponseDTO(
        id=imp.id,
        process_number=imp.process_number,
        supplier_name=imp.supplier_name,
        bl_number=imp.bl_number,
        container_number=imp.container_number,
        origin_port=imp.origin_port,
        destination_port=imp.destination_port,
        status=imp.status,
        eta=imp.eta,
        total_usd=imp.total_usd,
        landed_cost_brl=imp.landed_cost_brl,
        created_at=imp.created_at
    )


@router.get("", response_model=List[ImportProcessResponseDTO])
async def list_import_processes(session: AsyncSession = Depends(get_db_session)):
    stmt = select(ImportProcessORM).order_by(ImportProcessORM.id.desc())
    res = await session.execute(stmt)
    return [
        ImportProcessResponseDTO(
            id=i.id,
            process_number=i.process_number,
            supplier_name=i.supplier_name,
            bl_number=i.bl_number,
            container_number=i.container_number,
            origin_port=i.origin_port,
            destination_port=i.destination_port,
            status=i.status,
            eta=i.eta,
            total_usd=i.total_usd,
            landed_cost_brl=i.landed_cost_brl,
            created_at=i.created_at
        )
        for i in res.scalars().all()
    ]
