"""Roteadores FastAPI da camada de Apresentação para Cadastros Mestres."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db_session
from src.modules.cadastros_mestres.application.dtos.product_dto import (
    ProductCreateDTO, ProductResponseDTO,
    CustomerCreateDTO, CustomerResponseDTO,
    VehicleCreateDTO, VehicleResponseDTO
)
from src.modules.cadastros_mestres.application.use_cases.cadastros_use_cases import (
    ProductUseCases, CustomerUseCases, VehicleUseCases
)
from src.modules.cadastros_mestres.infrastructure.repositories.sqlalchemy_repos import (
    SQLAlchemyProductRepository, SQLAlchemyCustomerRepository, SQLAlchemyVehicleRepository
)

router = APIRouter(prefix="/api/v1", tags=["Cadastros Mestres"])


# ==============================================================================
# PRODUTOS (CRUD)
# ==============================================================================
@router.post("/products", response_model=ProductResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_product(
    dto: ProductCreateDTO,
    session: AsyncSession = Depends(get_db_session)
):
    use_case = ProductUseCases(SQLAlchemyProductRepository(session))
    try:
        return await use_case.create_product(dto)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/products", response_model=List[ProductResponseDTO])
async def list_products(session: AsyncSession = Depends(get_db_session)):
    use_case = ProductUseCases(SQLAlchemyProductRepository(session))
    return await use_case.list_products()


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, session: AsyncSession = Depends(get_db_session)):
    use_case = ProductUseCases(SQLAlchemyProductRepository(session))
    success = await use_case.delete_product(product_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado.")


# ==============================================================================
# CLIENTES (CRUD)
# ==============================================================================
@router.post("/customers", response_model=CustomerResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_customer(
    dto: CustomerCreateDTO,
    session: AsyncSession = Depends(get_db_session)
):
    use_case = CustomerUseCases(SQLAlchemyCustomerRepository(session))
    try:
        return await use_case.create_customer(dto)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/customers", response_model=List[CustomerResponseDTO])
async def list_customers(session: AsyncSession = Depends(get_db_session)):
    use_case = CustomerUseCases(SQLAlchemyCustomerRepository(session))
    return await use_case.list_customers()


@router.delete("/customers/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(customer_id: int, session: AsyncSession = Depends(get_db_session)):
    use_case = CustomerUseCases(SQLAlchemyCustomerRepository(session))
    success = await use_case.delete_customer(customer_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado.")


# ==============================================================================
# VEÍCULOS / CAMINHÕES (CRUD)
# ==============================================================================
@router.post("/vehicles", response_model=VehicleResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_vehicle(
    dto: VehicleCreateDTO,
    session: AsyncSession = Depends(get_db_session)
):
    use_case = VehicleUseCases(SQLAlchemyVehicleRepository(session))
    try:
        return await use_case.create_vehicle(dto)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/vehicles", response_model=List[VehicleResponseDTO])
async def list_vehicles(session: AsyncSession = Depends(get_db_session)):
    use_case = VehicleUseCases(SQLAlchemyVehicleRepository(session))
    return await use_case.list_vehicles()


@router.delete("/vehicles/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vehicle(vehicle_id: int, session: AsyncSession = Depends(get_db_session)):
    use_case = VehicleUseCases(SQLAlchemyVehicleRepository(session))
    success = await use_case.delete_vehicle(vehicle_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Veículo não encontrado.")
