#!/usr/bin/env python3
"""
Simulación no destructiva para poblar el dashboard de satélites.
No realiza uploads reales: sólo genera vídeos dummy con LongCat (modo DUMMY_MODE)
y programa/marca tareas como completadas localmente para poblar estadísticas.
"""
import asyncio
import json
import random
from pathlib import Path
from datetime import datetime, timedelta

from ml_core.satellite_manager import create_satellite_manager
from ml_core.video_generation.longcat_generator import create_video_generator


OUTPUT_DIR = Path("data/simulated_dashboard")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


async def simulate(days: int = 7):
    manager = create_satellite_manager()
    generator = create_video_generator()

    # Inicializar generador (dummy)
    await generator.initialize()

    satellites = list(manager.satellites.values())
    start_time = datetime.now()

    simulated_tasks = []

    # Para cada día y cada satélite, generar según la frecuencia configurada
    for day in range(days):
        for sat in satellites:
            # número de uploads por día según upload_frequency
            uploads_today = sat.upload_frequency
            for i in range(uploads_today):
                prompt = sat.video_config.get("default_prompt") or f"{sat.name} - simulated content"

                # Generar video dummy (no red network calls in dummy mode)
                result = await generator.generate_text_to_video(prompt=prompt, duration=6)

                # Programar upload (esto sólo crea una tarea en la cola, no sube a YouTube)
                task = await manager.schedule_upload(
                    video_path=result.video_path,
                    audio_path=f"data/audio/simulated/{sat.niche}_track.mp3",
                    niche=sat.niche
                )

                # Simular tiempo de publicación: usar horarios del satélite, desplazados por day
                scheduled = task.scheduled_time + timedelta(days=day)
                task.scheduled_time = scheduled

                # Marcar completado localmente (sin ejecutar upload real)
                task.status = "completed"
                sat.total_uploads += 1

                # Generar vistas simuladas según nicho/estrategia
                base_views = random.randint(50, 800)
                strategy_bonus = int(base_views * (0.1 + random.random()))
                views = base_views + strategy_bonus
                sat.total_views += views

                simulated_tasks.append({
                    "satellite": sat.id,
                    "name": sat.name,
                    "video_path": result.video_path,
                    "scheduled_time": scheduled.isoformat(),
                    "status": task.status,
                    "views": views,
                })

    # Guardar resultados
    stats = manager.get_statistics()
    stats["simulated_tasks_count"] = len(simulated_tasks)
    stats["simulated_period_days"] = days

    with open(OUTPUT_DIR / "satellite_stats.json", "w") as f:
        json.dump({"stats": stats, "tasks": simulated_tasks}, f, indent=2, default=str)

    print(f"✅ Simulación completada: {len(simulated_tasks)} tasks creadas for {len(satellites)} satellites")
    print(f"📁 Stats written to {OUTPUT_DIR / 'satellite_stats.json'}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Simulate satellite dashboard data (non-destructive)")
    parser.add_argument("--days", type=int, default=7, help="Days to simulate (default: 7)")
    args = parser.parse_args()

    asyncio.run(simulate(days=args.days))
