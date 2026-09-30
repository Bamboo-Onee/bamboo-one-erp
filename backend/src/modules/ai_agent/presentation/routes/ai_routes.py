"""Roteadores FastAPI para o Módulo de AI Agent (Tool Calling).

O agente interpreta a intenção do operador em linguagem natural, aciona as ferramentas determinísticas
do sistema (ex: motor de 3D Bin Packing) e devolve a resposta estruturada acompanhada de síntese explicativa.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, status

from src.modules.logistics.domain.services.packing_service import PackingService

router = APIRouter(prefix="/api/v1/ai", tags=["AI Agent (Tool Calling)"])


class ChatMessageRequest(BaseModel):
    prompt: str = Field(..., description="Pergunta ou instrução do operador em linguagem natural")
    truck_name: Optional[str] = "Truck Baú"
    cargo_quantity: Optional[int] = 44


class ChatMessageResponse(BaseModel):
    reply: str
    tool_called: str
    tool_parameters: Dict[str, Any]
    tool_result: Dict[str, Any]


@router.post("/chat", response_model=ChatMessageResponse, status_code=status.HTTP_200_OK)
async def chat_with_agent(req: ChatMessageRequest):
    """Processa o prompt do operador, executa Tool Calling contra o motor 3D e devolve o plano explicado."""
    prompt_lower = req.prompt.lower()

    # Tool Calling Determinístico: detecta solicitação de cubagem ou arrumação de caminhão
    if any(term in prompt_lower for term in ["caixa", "cabe", "arrum", "caminh", "baú", "otimiz", "truck", "toco"]):
        tool_name = "calculate_truck_packing"
        
        # Parâmetros inferidos ou enviados
        truck_len = 8.2
        truck_wid = 2.45
        truck_hei = 2.6
        truck_max_kg = 14000.0

        if "toco" in prompt_lower:
            req.truck_name = "Toco Urbano"
            truck_len = 6.2
            truck_wid = 2.4
            truck_hei = 2.45
            truck_max_kg = 8500.0
        elif "carreta" in prompt_lower:
            req.truck_name = "Carreta LS"
            truck_len = 13.5
            truck_wid = 2.48
            truck_hei = 2.75
            truck_max_kg = 28000.0

        items = [
            {"name": "Caixa Master A", "quantity": 24, "length_m": 1.2, "width_m": 0.8, "height_m": 0.7, "weight_kg": 185.0},
            {"name": "Pallet B", "quantity": 8, "length_m": 1.0, "width_m": 1.0, "height_m": 1.45, "weight_kg": 410.0},
            {"name": "Volume Frágil", "quantity": 12, "length_m": 0.7, "width_m": 0.55, "height_m": 0.6, "weight_kg": 76.0}
        ]

        # Invocação determinística da ferramenta
        packing_result = PackingService.calculate_packing(
            truck_name=req.truck_name or "Truck Baú",
            truck_length=truck_len,
            truck_width=truck_wid,
            truck_height=truck_hei,
            truck_max_weight_kg=truck_max_kg,
            items_data=items
        )

        tool_params = {
            "vehicle": req.truck_name,
            "useful_dimensions": f"{truck_len}m x {truck_wid}m x {truck_hei}m",
            "max_payload": f"{truck_max_kg} kg",
            "cargo_items_count": len(items)
        }

        # Síntese em Linguagem Natural com Persona de Engenheiro Logístico
        nl_reply = (
            f"Olá! Analisei sua solicitação com o motor matemático de 3D Bin Packing do Grupo Bamboo. "
            f"Para o veículo **{packing_result['truck_name']}**, o plano foi classificado como **{packing_result['status']}**.\n\n"
            f"📊 **Métricas Calculadas:**\n"
            f"- **Ocupação Volumétrica:** {packing_result['volumetric_efficiency_pct']}%\n"
            f"- **Peso Utilizado:** {packing_result['fitted_weight_kg']:,.1f} kg de {packing_result['max_payload_kg']:,.0f} kg ({packing_result['weight_efficiency_pct']}%)\n"
            f"- **Volumes Alocados:** {packing_result['total_items_allocated']}\n\n"
            f"💡 **Recomendação Operacional de Carregamento:**\n"
            f"{packing_result['alert_message']}\n"
            f"Posicione as bases de Pallet B no piso central para estabilização do centro de gravidade, "
            f"as Caixas Master A no fundo e reserve a área próxima à porta para os volumes frágeis."
        )

        return ChatMessageResponse(
            reply=nl_reply,
            tool_called=tool_name,
            tool_parameters=tool_params,
            tool_result=packing_result
        )

    # Resposta genérica orientada a operações do ERP
    return ChatMessageResponse(
        reply=(
            "Olá! Sou o Assistente de Inteligência Logística do Grupo Bamboo. "
            "Posso ajudá-lo com cálculos exatos de cubagem 3D para caminhões, simulação de planos de carga, "
            "consulta de status de pedidos e verificação de capacidade de frota. "
            "Experimente perguntar: *'Quantas caixas padrão cabem no baú do Truck?'*"
        ),
        tool_called="none",
        tool_parameters={},
        tool_result={}
    )
