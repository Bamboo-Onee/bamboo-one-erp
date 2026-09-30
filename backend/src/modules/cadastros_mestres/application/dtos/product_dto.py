"""DTOs (Data Transfer Objects) da camada de Aplicação para Cadastros Mestres."""

from typing import Optional
from pydantic import BaseModel, Field


class ProductCreateDTO(BaseModel):
    sku: str = Field(..., description="SKU único do item")
    name: str = Field(..., description="Nome comercial")
    category: str = Field(default="Geral")
    price: float = Field(default=0.0, ge=0)
    weight_kg: float = Field(..., gt=0, description="Peso em kg")
    length_m: float = Field(..., gt=0, description="Comprimento em metros")
    width_m: float = Field(..., gt=0, description="Largura em metros")
    height_m: float = Field(..., gt=0, description="Altura em metros")
    description: Optional[str] = None
    stackable: bool = True
    max_stack_layers: int = 2
    can_rotate: bool = True
    fragile: bool = False


class ProductResponseDTO(ProductCreateDTO):
    id: int
    volume_m3: float
    is_active: bool


class CustomerCreateDTO(BaseModel):
    name: str
    document: str
    email: str
    phone: str
    delivery_address: str
    credit_limit: float = 0.0


class CustomerResponseDTO(CustomerCreateDTO):
    id: int
    is_active: bool


class VehicleCreateDTO(BaseModel):
    plate: str
    model: str
    body_type: str = "Baú"
    length_m: float = Field(..., gt=0)
    width_m: float = Field(..., gt=0)
    height_m: float = Field(..., gt=0)
    max_payload_kg: float = Field(..., gt=0)


class VehicleResponseDTO(VehicleCreateDTO):
    id: int
    useful_volume_m3: float
    is_active: bool
