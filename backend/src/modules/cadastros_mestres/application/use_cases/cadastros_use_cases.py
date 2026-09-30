"""Casos de Uso da Camada de Aplicação para Cadastros Mestres."""

from typing import List
from src.modules.cadastros_mestres.domain.entities.product import Product, Dimensions
from src.modules.cadastros_mestres.domain.entities.customer import Customer
from src.modules.cadastros_mestres.domain.entities.vehicle import Vehicle
from src.modules.cadastros_mestres.domain.repositories.interfaces import (
    ProductRepositoryInterface, CustomerRepositoryInterface, VehicleRepositoryInterface
)
from src.modules.cadastros_mestres.application.dtos.product_dto import (
    ProductCreateDTO, ProductResponseDTO,
    CustomerCreateDTO, CustomerResponseDTO,
    VehicleCreateDTO, VehicleResponseDTO
)


class ProductUseCases:
    def __init__(self, repo: ProductRepositoryInterface):
        self.repo = repo

    async def create_product(self, dto: ProductCreateDTO) -> ProductResponseDTO:
        existing = await self.repo.get_by_sku(dto.sku)
        if existing:
            raise ValueError(f"Já existe um produto com o SKU '{dto.sku}'.")

        domain_product = Product(
            sku=dto.sku,
            name=dto.name,
            category=dto.category,
            price=dto.price,
            weight_kg=dto.weight_kg,
            dimensions=Dimensions(
                length=dto.length_m,
                width=dto.width_m,
                height=dto.height_m
            ),
            description=dto.description,
            stackable=dto.stackable,
            max_stack_layers=dto.max_stack_layers,
            can_rotate=dto.can_rotate,
            fragile=dto.fragile
        )

        saved = await self.repo.create(domain_product)
        return ProductResponseDTO(
            id=saved.id or 0,
            sku=saved.sku,
            name=saved.name,
            category=saved.category,
            price=saved.price,
            weight_kg=saved.weight_kg,
            length_m=saved.dimensions.length,
            width_m=saved.dimensions.width,
            height_m=saved.dimensions.height,
            volume_m3=saved.volume_m3,
            description=saved.description,
            stackable=saved.stackable,
            max_stack_layers=saved.max_stack_layers,
            can_rotate=saved.can_rotate,
            fragile=saved.fragile,
            is_active=saved.is_active
        )

    async def list_products(self) -> List[ProductResponseDTO]:
        products = await self.repo.list_all()
        return [
            ProductResponseDTO(
                id=p.id or 0,
                sku=p.sku,
                name=p.name,
                category=p.category,
                price=p.price,
                weight_kg=p.weight_kg,
                length_m=p.dimensions.length,
                width_m=p.dimensions.width,
                height_m=p.dimensions.height,
                volume_m3=p.volume_m3,
                description=p.description,
                stackable=p.stackable,
                max_stack_layers=p.max_stack_layers,
                can_rotate=p.can_rotate,
                fragile=p.fragile,
                is_active=p.is_active
            )
            for p in products
        ]

    async def delete_product(self, product_id: int) -> bool:
        return await self.repo.delete(product_id)


class CustomerUseCases:
    def __init__(self, repo: CustomerRepositoryInterface):
        self.repo = repo

    async def create_customer(self, dto: CustomerCreateDTO) -> CustomerResponseDTO:
        existing = await self.repo.get_by_document(dto.document)
        if existing:
            raise ValueError(f"Já existe cliente com o documento '{dto.document}'.")

        domain_cust = Customer(
            name=dto.name,
            document=dto.document,
            email=dto.email,
            phone=dto.phone,
            delivery_address=dto.delivery_address,
            credit_limit=dto.credit_limit
        )

        saved = await self.repo.create(domain_cust)
        return CustomerResponseDTO(
            id=saved.id or 0,
            name=saved.name,
            document=saved.document,
            email=saved.email,
            phone=saved.phone,
            delivery_address=saved.delivery_address,
            credit_limit=saved.credit_limit,
            is_active=saved.is_active
        )

    async def list_customers(self) -> List[CustomerResponseDTO]:
        customers = await self.repo.list_all()
        return [
            CustomerResponseDTO(
                id=c.id or 0,
                name=c.name,
                document=c.document,
                email=c.email,
                phone=c.phone,
                delivery_address=c.delivery_address,
                credit_limit=c.credit_limit,
                is_active=c.is_active
            )
            for c in customers
        ]

    async def delete_customer(self, customer_id: int) -> bool:
        return await self.repo.delete(customer_id)


class VehicleUseCases:
    def __init__(self, repo: VehicleRepositoryInterface):
        self.repo = repo

    async def create_vehicle(self, dto: VehicleCreateDTO) -> VehicleResponseDTO:
        existing = await self.repo.get_by_plate(dto.plate)
        if existing:
            raise ValueError(f"Já existe veículo com a placa '{dto.plate}'.")

        domain_veh = Vehicle(
            plate=dto.plate,
            model=dto.model,
            body_type=dto.body_type,
            length_m=dto.length_m,
            width_m=dto.width_m,
            height_m=dto.height_m,
            max_payload_kg=dto.max_payload_kg
        )

        saved = await self.repo.create(domain_veh)
        return VehicleResponseDTO(
            id=saved.id or 0,
            plate=saved.plate,
            model=saved.model,
            body_type=saved.body_type,
            length_m=saved.length_m,
            width_m=saved.width_m,
            height_m=saved.height_m,
            max_payload_kg=saved.max_payload_kg,
            useful_volume_m3=saved.useful_volume_m3,
            is_active=saved.is_active
        )

    async def list_vehicles(self) -> List[VehicleResponseDTO]:
        vehicles = await self.repo.list_all()
        return [
            VehicleResponseDTO(
                id=v.id or 0,
                plate=v.plate,
                model=v.model,
                body_type=v.body_type,
                length_m=v.length_m,
                width_m=v.width_m,
                height_m=v.height_m,
                max_payload_kg=v.max_payload_kg,
                useful_volume_m3=v.useful_volume_m3,
                is_active=v.is_active
            )
            for v in vehicles
        ]

    async def delete_vehicle(self, vehicle_id: int) -> bool:
        return await self.repo.delete(vehicle_id)
