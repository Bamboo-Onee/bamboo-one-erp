"""Entidade de Domínio Pura: Produto (Product).

Totalmente desacoplada de frameworks ou ORMs, contendo invariantes de negócio e validações lógicas.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Dimensions:
    """Value Object: Dimensões tridimensionais externas (em metros)."""
    length: float
    width: float
    height: float

    def __post_init__(self):
        if self.length <= 0 or self.width <= 0 or self.height <= 0:
            raise ValueError("Dimensões devem ser números positivos estritos.")

    @property
    def volume_m3(self) -> float:
        """Volume cúbico em metros cúbicos (C × L × A)."""
        return round(self.length * self.width * self.height, 4)


@dataclass
class Product:
    """Entidade central de Produto consolidando aspectos comerciais e de cubagem logística."""
    sku: str
    name: str
    category: str
    price: float
    weight_kg: float
    dimensions: Dimensions
    description: Optional[str] = None
    stackable: bool = True
    max_stack_layers: int = 2
    can_rotate: bool = True
    fragile: bool = False
    is_active: bool = True
    id: Optional[int] = None

    def __post_init__(self):
        if not self.sku or not self.sku.strip():
            raise ValueError("O SKU do produto não pode ser vazio.")
        if not self.name or not self.name.strip():
            raise ValueError("O nome do produto não pode ser vazio.")
        if self.price < 0:
            raise ValueError("O preço do produto não pode ser negativo.")
        if self.weight_kg <= 0:
            raise ValueError("O peso do produto deve ser maior que zero.")

    @property
    def volume_m3(self) -> float:
        return self.dimensions.volume_m3
