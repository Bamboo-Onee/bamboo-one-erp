"""Entidade de Domínio: Veículo / Caminhão (Vehicle)."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Vehicle:
    plate: str
    model: str
    body_type: str
    length_m: float
    width_m: float
    height_m: float
    max_payload_kg: float
    is_active: bool = True
    id: Optional[int] = None

    def __post_init__(self):
        if not self.plate or not self.plate.strip():
            raise ValueError("Placa do veículo é obrigatória.")
        if self.length_m <= 0 or self.width_m <= 0 or self.height_m <= 0:
            raise ValueError("Dimensões úteis do baú devem ser positivas.")
        if self.max_payload_kg <= 0:
            raise ValueError("Carga útil máxima deve ser maior que zero.")

    @property
    def useful_volume_m3(self) -> float:
        return round(self.length_m * self.width_m * self.height_m, 3)
