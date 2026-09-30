"""Roteadores FastAPI para o Módulo Financeiro (Contas a Pagar e Contas a Receber)."""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db_session
from src.core.models import FinancialEntryORM

router = APIRouter(prefix="/api/v1/finance", tags=["Financeiro"])


class FinancialEntryCreateDTO(BaseModel):
    entry_type: str = Field(..., description="PAGAR ou RECEBER")
    description: str
    entity_name: str
    category: str = "Operacional"
    amount: float = Field(..., gt=0)
    due_date: str = "10/09/2026"
    status: str = "Pendente"


class FinancialEntryResponseDTO(FinancialEntryCreateDTO):
    id: int
    created_at: Optional[datetime] = None


class FinancialSummaryDTO(BaseModel):
    total_payable: float
    total_receivable: float
    projected_balance: float


@router.post("", response_model=FinancialEntryResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_financial_entry(
    dto: FinancialEntryCreateDTO,
    session: AsyncSession = Depends(get_db_session)
):
    entry = FinancialEntryORM(
        entry_type=dto.entry_type.upper(),
        description=dto.description,
        entity_name=dto.entity_name,
        category=dto.category,
        amount=dto.amount,
        due_date=dto.due_date,
        status=dto.status
    )
    session.add(entry)
    await session.commit()
    await session.refresh(entry)
    return FinancialEntryResponseDTO(
        id=entry.id,
        entry_type=entry.entry_type,
        description=entry.description,
        entity_name=entry.entity_name,
        category=entry.category,
        amount=entry.amount,
        due_date=entry.due_date,
        status=entry.status,
        created_at=entry.created_at
    )


@router.get("", response_model=List[FinancialEntryResponseDTO])
async def list_financial_entries(session: AsyncSession = Depends(get_db_session)):
    stmt = select(FinancialEntryORM).order_by(FinancialEntryORM.id.desc())
    res = await session.execute(stmt)
    entries = res.scalars().all()

    if not entries:
        seed = [
            FinancialEntryORM(entry_type="PAGAR", description="Fornecedor de Pallets", entity_name="Bamboo Trade", category="Compras", amount=18430.0, due_date="15/09/2026", status="Pendente"),
            FinancialEntryORM(entry_type="PAGAR", description="Frete Internacional Santos", entity_name="Maersk Line", category="Importação", amount=12850.0, due_date="18/09/2026", status="Pendente"),
            FinancialEntryORM(entry_type="RECEBER", description="Venda Comercial Atlântico", entity_name="Cliente Atlântico", category="Vendas", amount=78200.0, due_date="20/09/2026", status="Pendente"),
            FinancialEntryORM(entry_type="RECEBER", description="Venda Distribuidora Sul", entity_name="Distribuidora Sul", category="Vendas", amount=43150.0, due_date="22/09/2026", status="Pendente")
        ]
        for it in seed:
            session.add(it)
        await session.commit()
        stmt = select(FinancialEntryORM).order_by(FinancialEntryORM.id.desc())
        res = await session.execute(stmt)
        entries = res.scalars().all()

    return [
        FinancialEntryResponseDTO(
            id=e.id,
            entry_type=e.entry_type,
            description=e.description,
            entity_name=e.entity_name,
            category=e.category,
            amount=e.amount,
            due_date=e.due_date,
            status=e.status,
            created_at=e.created_at
        )
        for e in entries
    ]


@router.get("/summary", response_model=FinancialSummaryDTO)
async def get_financial_summary(session: AsyncSession = Depends(get_db_session)):
    stmt = select(FinancialEntryORM)
    res = await session.execute(stmt)
    entries = res.scalars().all()

    payable = sum(e.amount for e in entries if e.entry_type == "PAGAR")
    receivable = sum(e.amount for e in entries if e.entry_type == "RECEBER")

    return FinancialSummaryDTO(
        total_payable=round(payable, 2),
        total_receivable=round(receivable, 2),
        projected_balance=round(receivable - payable, 2)
    )
