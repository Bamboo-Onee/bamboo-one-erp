"""Entidade de Domínio: Cliente (Customer)."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Customer:
    name: str
    document: str  # CPF ou CNPJ
    email: str
    phone: str
    delivery_address: str
    credit_limit: float = 0.0
    is_active: bool = True
    id: Optional[int] = None

    def __post_init__(self):
        if not self.name or not self.name.strip():
            raise ValueError("Nome do cliente é obrigatório.")
        if not self.document or not self.document.strip():
            raise ValueError("CPF/CNPJ do cliente é obrigatório.")
        if self.credit_limit < 0:
            raise ValueError("Limite de crédito não pode ser negativo.")
