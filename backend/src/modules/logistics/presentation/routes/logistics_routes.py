"""Roteadores FastAPI para o Módulo Logístico e Otimizador de Carga 3D."""

from typing import List, Dict, Any
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, status

from src.core.models import UserORM
from src.modules.auth.presentation.routes.auth_routes import require_roles
from src.modules.logistics.domain.services.packing_service import PackingService

router = APIRouter(prefix="/api/v1/logistics", tags=["Logística & Otimizador 3D"])


class CargoItemInput(BaseModel):
    name: str = Field(..., min_length=1, max_length=120, description="Nome ou SKU do item")
    quantity: int = Field(default=1, ge=1, le=500, description="Quantidade de volumes (máx. 500 por SKU)")
    length_m: float = Field(..., gt=0, le=30.0, description="Comprimento em metros")
    width_m: float = Field(..., gt=0, le=30.0, description="Largura em metros")
    height_m: float = Field(..., gt=0, le=30.0, description="Altura em metros")
    weight_kg: float = Field(..., gt=0, le=50000.0, description="Peso unitário em kg")


class PackSimulationRequest(BaseModel):
    truck_name: str = Field(default="Truck Baú")
    truck_length: float = Field(default=8.2, gt=0, le=30.0)
    truck_width: float = Field(default=2.45, gt=0, le=10.0)
    truck_height: float = Field(default=2.6, gt=0, le=10.0)
    truck_max_weight_kg: float = Field(default=14000.0, gt=0, le=100000.0)
    items: List[CargoItemInput] = Field(..., min_length=1, max_length=50)


class FleetParallelSimulationRequest(BaseModel):
    items: List[CargoItemInput] = Field(..., min_length=1, max_length=50)


@router.post("/pack-simulation", status_code=status.HTTP_200_OK)
async def simulate_packing(
    req: PackSimulationRequest,
    current_user: UserORM = Depends(require_roles(["LOGISTICA"]))
) -> Dict[str, Any]:
    """Simula o cálculo matemático de 3D Bin Packing retornando taxa de ocupação e posições X, Y, Z."""
    items_dicts = [item.model_dump() for item in req.items]
    return await PackingService.calculate_packing_async(
        truck_name=req.truck_name,
        truck_length=req.truck_length,
        truck_width=req.truck_width,
        truck_height=req.truck_height,
        truck_max_weight_kg=req.truck_max_weight_kg,
        items_data=items_dicts
    )


@router.post("/pack-fleet-parallel", status_code=status.HTTP_200_OK)
async def simulate_fleet_parallel(
    req: FleetParallelSimulationRequest,
    current_user: UserORM = Depends(require_roles(["LOGISTICA"]))
) -> Dict[str, Any]:
    """Executa simulação paralela multi-core em toda a frota de caminhões e recomenda o melhor veículo."""
    items_dicts = [item.model_dump() for item in req.items]
    return await PackingService.calculate_fleet_parallel_async(items_dicts)
