"""Motor Matemático Determinístico de 3D Bin Packing.

Executa o algoritmo combinatório de empacotamento espacial tridimensional, calculando:
- Posicionamento exato (X, Y, Z) e orientação de cada volume
- Taxa percentual de ocupação volumétrica (%)
- Taxa percentual de utilização de carga/peso (%)
- Detecção e lista detalhada de volumes excedentes (que não couberam)
"""

from typing import List, Dict, Any
from py3dbp import Packer, Bin, Item


class PackingService:
    @staticmethod
    def calculate_packing(
        truck_name: str,
        truck_length: float,
        truck_width: float,
        truck_height: float,
        truck_max_weight_kg: float,
        items_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calcula o empacotamento 3D tridimensional exato."""
        packer = Packer()

        # py3dbp signature: Bin(name, width, height, depth, max_weight)
        # width = largura (m), height = altura (m), depth = comprimento (m)
        scale = 100.0  # 1 metro = 100 cm para cálculo com inteiros/floats
        b_wid = truck_width * scale
        b_hei = truck_height * scale
        b_dep = truck_length * scale
        b_max_w = truck_max_weight_kg

        truck_bin = Bin(
            name=truck_name,
            width=b_wid,
            height=b_hei,
            depth=b_dep,
            max_weight=b_max_w
        )
        packer.add_bin(truck_bin)

        total_items_count = 0
        total_cargo_volume = 0.0
        total_cargo_weight = 0.0

        for it in items_data:
            qty = it.get("quantity", 1)
            name = it.get("name", "Item")
            dep = float(it.get("length_m", 1.0)) * scale
            wid = float(it.get("width_m", 1.0)) * scale
            hei = float(it.get("height_m", 1.0)) * scale
            weight = float(it.get("weight_kg", 10.0))

            for i in range(qty):
                total_items_count += 1
                total_cargo_volume += (dep / scale) * (wid / scale) * (hei / scale)
                total_cargo_weight += weight
                item_name = f"{name} #{i+1}"
                packer.add_item(Item(name=item_name, width=wid, height=hei, depth=dep, weight=weight))

        # Executa otimização
        packer.pack(bigger_first=True)

        evaluated_bin = packer.bins[0]
        fitted_items = []
        fitted_weight = 0.0
        fitted_volume = 0.0

        for fit in evaluated_bin.items:
            fitted_weight += float(fit.weight)
            v_m3 = (float(fit.width) / scale) * (float(fit.height) / scale) * (float(fit.depth) / scale)
            fitted_volume += v_m3
            fitted_items.append({
                "name": fit.name,
                "position": [
                    round(float(fit.position[0]) / scale, 3),
                    round(float(fit.position[1]) / scale, 3),
                    round(float(fit.position[2]) / scale, 3)
                ],
                "dimensions": [
                    round(float(fit.depth) / scale, 3),
                    round(float(fit.width) / scale, 3),
                    round(float(fit.height) / scale, 3)
                ],
                "weight_kg": float(fit.weight)
            })

        unfitted_items = [unfit.name for unfit in evaluated_bin.unfitted_items]

        truck_vol_m3 = truck_length * truck_width * truck_height
        vol_efficiency_pct = round((fitted_volume / truck_vol_m3) * 100, 1) if truck_vol_m3 > 0 else 0.0
        weight_efficiency_pct = round((fitted_weight / truck_max_weight_kg) * 100, 1) if truck_max_weight_kg > 0 else 0.0

        is_viable = len(unfitted_items) == 0 and fitted_weight <= truck_max_weight_kg

        if not is_viable:
            status_text = "Inviável"
            alert_message = f"Excedeu capacidade. {len(unfitted_items)} volume(s) não couberam ou excederam o peso de {truck_max_weight_kg} kg."
        elif vol_efficiency_pct < 60.0:
            status_text = "Viável (Baixa Ocupação)"
            alert_message = f"Todos os {len(fitted_items)} volumes couberam, porém há {round(100 - vol_efficiency_pct, 1)}% de capacidade ociosa."
        else:
            status_text = "Viável"
            alert_message = f"Plano excelente! {len(fitted_items)} volumes alocados com {vol_efficiency_pct}% de ocupação volumétrica."

        return {
            "truck_name": truck_name,
            "status": status_text,
            "is_viable": is_viable,
            "volumetric_efficiency_pct": vol_efficiency_pct,
            "weight_efficiency_pct": weight_efficiency_pct,
            "fitted_weight_kg": round(fitted_weight, 2),
            "max_payload_kg": truck_max_weight_kg,
            "total_items_allocated": f"{len(fitted_items)}/{total_items_count}",
            "unfitted_items_count": len(unfitted_items),
            "unfitted_items": unfitted_items,
            "alert_message": alert_message,
            "allocated_boxes": fitted_items
        }
