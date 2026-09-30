"""Roteadores FastAPI para o Módulo de Recursos Humanos (RH)."""

from typing import List
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db_session
from src.core.models import EmployeeORM

router = APIRouter(prefix="/api/v1/employees", tags=["Recursos Humanos"])


class EmployeeCreateDTO(BaseModel):
    name: str
    cpf: str
    role: str
    department: str
    salary: float = Field(..., gt=0)
    admission_date: str = "01/02/2024"
    status: str = "Ativo"


class EmployeeResponseDTO(EmployeeCreateDTO):
    id: int


@router.post("", response_model=EmployeeResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_employee(
    dto: EmployeeCreateDTO,
    session: AsyncSession = Depends(get_db_session)
):
    emp = EmployeeORM(
        name=dto.name,
        cpf=dto.cpf,
        role=dto.role,
        department=dto.department,
        salary=dto.salary,
        admission_date=dto.admission_date,
        status=dto.status
    )
    session.add(emp)
    await session.commit()
    await session.refresh(emp)
    return EmployeeResponseDTO(
        id=emp.id,
        name=emp.name,
        cpf=emp.cpf,
        role=emp.role,
        department=emp.department,
        salary=emp.salary,
        admission_date=emp.admission_date,
        status=emp.status
    )


@router.get("", response_model=List[EmployeeResponseDTO])
async def list_employees(session: AsyncSession = Depends(get_db_session)):
    stmt = select(EmployeeORM).order_by(EmployeeORM.id.desc())
    res = await session.execute(stmt)
    employees = res.scalars().all()

    if not employees:
        seed = [
            EmployeeORM(name="Marina Silva", cpf="111.222.333-44", role="Analista de Importação", department="Comércio Exterior", salary=6200.0, admission_date="15/03/2023", status="Ativo"),
            EmployeeORM(name="Carlos Eduardo", cpf="555.666.777-88", role="Supervisor de Estoque", department="Logística", salary=5400.0, admission_date="10/01/2022", status="Ativo"),
            EmployeeORM(name="Fernanda Lima", cpf="999.888.777-66", role="Coordenadora Financeira", department="Financeiro", salary=8900.0, admission_date="01/08/2021", status="Férias")
        ]
        for it in seed:
            session.add(it)
        await session.commit()
        stmt = select(EmployeeORM).order_by(EmployeeORM.id.desc())
        res = await session.execute(stmt)
        employees = res.scalars().all()

    return [
        EmployeeResponseDTO(
            id=e.id,
            name=e.name,
            cpf=e.cpf,
            role=e.role,
            department=e.department,
            salary=e.salary,
            admission_date=e.admission_date,
            status=e.status
        )
        for e in employees
    ]
