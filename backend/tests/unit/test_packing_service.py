"""Testes Unitários do Motor de 3D Bin Packing."""

from src.modules.logistics.domain.services.packing_service import PackingService


def test_packing_service_fits_small_cargo():
    """Valida se uma carga pequena cabe em um caminhão Truck com cálculo de coordenadas 3D."""
    items = [
        {"name": "Caixa Pequena", "quantity": 4, "length_m": 1.0, "width_m": 0.8, "height_m": 0.5, "weight_kg": 50.0}
    ]
    result = PackingService.calculate_packing(
        truck_name="Truck Baú",
        truck_length=8.2,
        truck_width=2.45,
        truck_height=2.6,
        truck_max_weight_kg=14000.0,
        items_data=items
    )

    assert result["is_viable"] is True
    assert result["total_items_allocated"] == "4/4"
    assert result["unfitted_items_count"] == 0
    assert len(result["allocated_boxes"]) == 4
    assert result["volumetric_efficiency_pct"] > 0.0


def test_packing_service_detects_overflow():
    """Valida se o motor identifica corretamente itens que excedem a capacidade volumétrica."""
    # Criamos caixas gigantes que não cabem
    items = [
        {"name": "Caixa Gigante", "quantity": 10, "length_m": 5.0, "width_m": 2.0, "height_m": 2.0, "weight_kg": 500.0}
    ]
    result = PackingService.calculate_packing(
        truck_name="Toco Pequeno",
        truck_length=5.0,
        truck_width=2.0,
        truck_height=2.0,
        truck_max_weight_kg=5000.0,
        items_data=items
    )

    assert result["is_viable"] is False
    assert result["unfitted_items_count"] > 0
