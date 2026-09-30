"""Testes Unitários de Domínio: Produto e Dimensões."""

import pytest
from src.modules.cadastros_mestres.domain.entities.product import Product, Dimensions


def test_product_dimensions_volume_calculation():
    """Valida o cálculo exato do volume cúbico (C × L × A)."""
    dim = Dimensions(length=1.2, width=0.8, height=0.7)
    assert dim.volume_m3 == 0.672


def test_product_negative_dimension_raises_error():
    """Garante que dimensões negativas ou zero disparam exceção de domínio."""
    with pytest.raises(ValueError, match="positivos estritos"):
        Dimensions(length=-1.0, width=0.8, height=0.7)


def test_product_valid_entity_creation():
    """Valida instanciação bem-sucedida de uma entidade de produto com invariantes válidos."""
    prod = Product(
        sku="BAM-0082",
        name="Caixa Master A",
        category="Embalagens",
        price=185.0,
        weight_kg=24.5,
        dimensions=Dimensions(length=1.2, width=0.8, height=0.7)
    )
    assert prod.sku == "BAM-0082"
    assert prod.volume_m3 == 0.672
    assert prod.is_active is True


def test_product_empty_sku_raises_error():
    """Garante que produtos sem SKU sejam rejeitados."""
    with pytest.raises(ValueError, match="SKU do produto não pode ser vazio"):
        Product(
            sku="   ",
            name="Produto Inválido",
            category="Geral",
            price=10.0,
            weight_kg=1.0,
            dimensions=Dimensions(length=1.0, width=1.0, height=1.0)
        )
