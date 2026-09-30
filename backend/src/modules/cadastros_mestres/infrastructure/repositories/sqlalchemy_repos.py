"""Implementações concretas dos repositórios utilizando SQLAlchemy 2.0 Async (Data Mapper)."""

from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.cadastros_mestres.domain.entities.product import Product, Dimensions
from src.modules.cadastros_mestres.domain.entities.customer import Customer
from src.modules.cadastros_mestres.domain.entities.vehicle import Vehicle
from src.modules.cadastros_mestres.domain.repositories.interfaces import (
    ProductRepositoryInterface, CustomerRepositoryInterface, VehicleRepositoryInterface
)
from src.modules.cadastros_mestres.infrastructure.models.orm_models import (
    ProductORM, CustomerORM, VehicleORM
)


class SQLAlchemyProductRepository(ProductRepositoryInterface):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, orm: ProductORM) -> Product:
        return Product(
            id=orm.id,
            sku=orm.sku,
            name=orm.name,
            category=orm.category,
            price=orm.price,
            weight_kg=orm.weight_kg,
            dimensions=Dimensions(
                length=orm.length_m,
                width=orm.width_m,
                height=orm.height_m
            ),
            description=orm.description,
            stackable=orm.stackable,
            max_stack_layers=orm.max_stack_layers,
            can_rotate=orm.can_rotate,
            fragile=orm.fragile,
            is_active=orm.is_active
        )

    async def create(self, product: Product) -> Product:
        orm = ProductORM(
            sku=product.sku,
            name=product.name,
            category=product.category,
            price=product.price,
            weight_kg=product.weight_kg,
            length_m=product.dimensions.length,
            width_m=product.dimensions.width,
            height_m=product.dimensions.height,
            description=product.description,
            stackable=product.stackable,
            max_stack_layers=product.max_stack_layers,
            can_rotate=product.can_rotate,
            fragile=product.fragile,
            is_active=product.is_active
        )
        self.session.add(orm)
        await self.session.flush()
        await self.session.refresh(orm)
        return self._to_domain(orm)

    async def get_by_sku(self, sku: str) -> Optional[Product]:
        stmt = select(ProductORM).where(ProductORM.sku == sku)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def list_all(self) -> List[Product]:
        stmt = select(ProductORM).order_by(ProductORM.id.desc())
        result = await self.session.execute(stmt)
        return [self._to_domain(orm) for orm in result.scalars().all()]

    async def delete(self, product_id: int) -> bool:
        stmt = delete(ProductORM).where(ProductORM.id == product_id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0


class SQLAlchemyCustomerRepository(CustomerRepositoryInterface):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, orm: CustomerORM) -> Customer:
        return Customer(
            id=orm.id,
            name=orm.name,
            document=orm.document,
            email=orm.email,
            phone=orm.phone,
            delivery_address=orm.delivery_address,
            credit_limit=orm.credit_limit,
            is_active=orm.is_active
        )

    async def create(self, customer: Customer) -> Customer:
        orm = CustomerORM(
            name=customer.name,
            document=customer.document,
            email=customer.email,
            phone=customer.phone,
            delivery_address=customer.delivery_address,
            credit_limit=customer.credit_limit,
            is_active=customer.is_active
        )
        self.session.add(orm)
        await self.session.flush()
        await self.session.refresh(orm)
        return self._to_domain(orm)

    async def get_by_document(self, document: str) -> Optional[Customer]:
        stmt = select(CustomerORM).where(CustomerORM.document == document)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def list_all(self) -> List[Customer]:
        stmt = select(CustomerORM).order_by(CustomerORM.id.desc())
        result = await self.session.execute(stmt)
        return [self._to_domain(orm) for orm in result.scalars().all()]

    async def delete(self, customer_id: int) -> bool:
        stmt = delete(CustomerORM).where(CustomerORM.id == customer_id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0


class SQLAlchemyVehicleRepository(VehicleRepositoryInterface):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, orm: VehicleORM) -> Vehicle:
        return Vehicle(
            id=orm.id,
            plate=orm.plate,
            model=orm.model,
            body_type=orm.body_type,
            length_m=orm.length_m,
            width_m=orm.width_m,
            height_m=orm.height_m,
            max_payload_kg=orm.max_payload_kg,
            is_active=orm.is_active
        )

    async def create(self, vehicle: Vehicle) -> Vehicle:
        orm = VehicleORM(
            plate=vehicle.plate,
            model=vehicle.model,
            body_type=vehicle.body_type,
            length_m=vehicle.length_m,
            width_m=vehicle.width_m,
            height_m=vehicle.height_m,
            max_payload_kg=vehicle.max_payload_kg,
            is_active=vehicle.is_active
        )
        self.session.add(orm)
        await self.session.flush()
        await self.session.refresh(orm)
        return self._to_domain(orm)

    async def get_by_plate(self, plate: str) -> Optional[Vehicle]:
        stmt = select(VehicleORM).where(VehicleORM.plate == plate)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def list_all(self) -> List[Vehicle]:
        stmt = select(VehicleORM).order_by(VehicleORM.id.desc())
        result = await self.session.execute(stmt)
        return [self._to_domain(orm) for orm in result.scalars().all()]

    async def delete(self, vehicle_id: int) -> bool:
        stmt = delete(VehicleORM).where(VehicleORM.id == vehicle_id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0
