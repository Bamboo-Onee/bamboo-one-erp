"""Motor Matemático Determinístico de 3D Bin Packing.

Executa o algoritmo combinatório de empacotamento espacial tridimensional, calculando:
- Posicionamento exato (X, Y, Z) e orientação de cada volume
- Taxa percentual de ocupação volumétrica (%)
- Taxa percentual de utilização de carga/peso (%)
- Detecção e lista detalhada de volumes excedentes (que não couberam)
- Execução assíncrona não-bloqueante e simulação paralela multi-core via ProcessPoolExecutor
"""

import asyncio
import multiprocessing
import os
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures.process import BrokenProcessPool
from typing import List, Dict, Any, Optional
from py3dbp import Packer, Bin, Item


class PackingService:
    _process_pool: Optional[ProcessPoolExecutor] = None

    @classmethod
    def init_process_pool(cls, max_workers: Optional[int] = None) -> ProcessPoolExecutor:
        """Inicializa o ProcessPoolExecutor global para paralelismo real de CPU (bypass do GIL)."""
        if cls._process_pool is None:
            workers = max_workers or min(os.cpu_count() or 2, 4)
            cls._process_pool = ProcessPoolExecutor(
                max_workers=workers,
                mp_context=multiprocessing.get_context("spawn")
            )
        return cls._process_pool

    @classmethod
    def shutdown_process_pool(cls) -> None:
        """Encerra graciosamente o pool de processos de CPU."""
        if cls._process_pool is not None:
            cls._process_pool.shutdown(wait=False, cancel_futures=True)
            cls._process_pool = None

    @classmethod
    def get_process_pool(cls) -> ProcessPoolExecutor:
        """Retorna o pool de processos ativo ou inicializa sob demanda."""
        if cls._process_pool is None:
            return cls.init_process_pool()
        return cls._process_pool

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

    @classmethod
    async def calculate_packing_async(
        cls,
        truck_name: str,
        truck_length: float,
        truck_width: float,
        truck_height: float,
        truck_max_weight_kg: float,
        items_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Executa o cálculo de 3D Bin Packing de forma não-bloqueante em ProcessPoolExecutor."""
        loop = asyncio.get_running_loop()
        try:
            return await loop.run_in_executor(
                cls.get_process_pool(),
                cls.calculate_packing,
                truck_name,
                truck_length,
                truck_width,
                truck_height,
                truck_max_weight_kg,
                items_data
            )
        except (BrokenProcessPool, RuntimeError):
            cls.shutdown_process_pool()
            return await asyncio.to_thread(
                cls.calculate_packing,
                truck_name,
                truck_length,
                truck_width,
                truck_height,
                truck_max_weight_kg,
                items_data
            )

    @classmethod
    async def calculate_fleet_parallel_async(
        cls,
        items_data: List[Dict[str, Any]],
        fleet_vehicles: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Executa simulação de empacotamento 3D em paralelo real multi-core para todos os veículos da frota."""
        if fleet_vehicles is None:
            fleet_vehicles = [
                {"truck_name": "Toco Urbano", "truck_length": 6.2, "truck_width": 2.4, "truck_height": 2.45, "truck_max_weight_kg": 8500.0},
                {"truck_name": "Truck Baú", "truck_length": 8.2, "truck_width": 2.45, "truck_height": 2.6, "truck_max_weight_kg": 14000.0},
                {"truck_name": "Carreta LS", "truck_length": 13.5, "truck_width": 2.48, "truck_height": 2.75, "truck_max_weight_kg": 28000.0},
            ]

        results = await asyncio.gather(
            *(
                cls.calculate_packing_async(
                    v["truck_name"],
                    v["truck_length"],
                    v["truck_width"],
                    v["truck_height"],
                    v["truck_max_weight_kg"],
                    items_data
                )
                for v in fleet_vehicles
            )
        )

        viable_plans = [r for r in results if r.get("is_viable")]
        if viable_plans:
            recommended = max(viable_plans, key=lambda r: r.get("volumetric_efficiency_pct", 0.0))
        else:
            recommended = max(
                results,
                key=lambda r: (len(r.get("allocated_boxes", [])), r.get("fitted_weight_kg", 0.0))
            )

        return {
            "parallel_workers_used": len(fleet_vehicles),
            "recommended_vehicle": recommended["truck_name"],
            "recommended_plan": recommended,
            "fleet_simulations": list(results)
        }
