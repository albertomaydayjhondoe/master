# 🛰️ SISTEMA DE CUENTAS SATÉLITE - GUÍA COMPLETA

## 🎯 ARQUITECTURA DEL SISTEMA

### Concepto
El sistema de cuentas satélite permite gestionar múltiples canales de YouTube de forma automatizada, distribuyendo contenido generado con IA (LongCat-Video) de manera inteligente y escalable.

```
                    ┌─────────────────┐
                    │  Cuenta Hub     │
                    │  (Principal)    │
                    │  UCgohgq...     │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
         ┌────▼────┐    ┌───▼────┐    ┌───▼────┐
         │ Sat 1   │    │ Sat 2  │    │ Sat 3  │
         │ Trap    │    │ Urban  │    │ HipHop │
         └─────────┘    └────────┘    └────────┘
              │              │              │
         ┌────▼────┐    ┌───▼────┐
         │ Sat 4   │    │ Sat 5  │
         │ Latino  │    │ Street │
         └─────────┘    └────────┘
```

---

## 🚀 SETUP RÁPIDO

### 1. Configuración Inicial

```bash
# El archivo de configuración ya está creado
config/satellite_accounts_config.json
```

### 2. Configurar Tokens OAuth

```bash
# Ejecutar configurador interactivo
python configure_satellite_tokens.py
```

**Proceso:**
1. Selecciona qué satélite(s) configurar
2. Se abrirá URL de autorización de Google
3. Inicia sesión con la cuenta del canal satélite
4. Autoriza la aplicación
5. Copia el código y pégalo en el script
6. Repite para cada satélite

### 3. Verificar Configuración

```python
from ml_core.satellite_manager import create_satellite_manager

manager = create_satellite_manager()
stats = manager.get_statistics()
print(stats)
```

---

## 📊 SATÉLITES CONFIGURADOS

### 🛰️ Satélite 1: "Trap Central"
- **Nicho:** Trap español/latino
- **Frecuencia:** 3 videos/día
- **Horarios:** 12:00, 18:00, 22:00 CET
- **Prompt:** "Urban artist in recording studio, purple neon lights, trap beat visualization"

### 🛰️ Satélite 2: "Urban Beats"
- **Nicho:** Reggaeton/Urban
- **Frecuencia:** 2 videos/día
- **Horarios:** 14:00, 20:00 CET
- **Prompt:** "Reggaeton dancer in miami beach club, tropical vibes, party atmosphere"

### 🛰️ Satélite 3: "Rap Underground"
- **Nicho:** Hip-Hop/Drill
- **Frecuencia:** 2 videos/día
- **Horarios:** 16:00, 23:00 CET
- **Prompt:** "Hip-hop artist in underground graffiti tunnel, raw street style"

### 🛰️ Satélite 4: "Latin Vibes"
- **Nicho:** Pop Latino/Urbano
- **Frecuencia:** 3 videos/día
- **Horarios:** 11:00, 17:00, 21:00 CET
- **Prompt:** "Latin pop artist in rooftop sunset, romantic mood, urban skyline"

### 🛰️ Satélite 5: "Street Sessions"
- **Nicho:** Freestyles/Sesiones
- **Frecuencia:** 2 videos/día
- **Horarios:** 15:00, 19:00 CET
- **Prompt:** "Freestyle rapper in street cypher, crowd energy, handheld camera"

---

## 💻 USO PROGRAMÁTICO

### Programar Upload Automático

```python
import asyncio
from ml_core.satellite_manager import create_satellite_manager

async def schedule_content():
    manager = create_satellite_manager()
    
    # Programar upload
    task = await manager.schedule_upload(
        video_path="data/generated_videos/video_001.mp4",
        audio_path="data/audio_library/trap/mi_track.mp3",
        niche="trap_spanish_latino",
        title="🔥 Mi Track | Trap Español 2025",
        description="Nuevo track de trap español...",
        tags=["trap", "español", "2025", "viral"]
    )
    
    print(f"✅ Upload programado para {task.scheduled_time}")

asyncio.run(schedule_content())
```

### Procesar Cola de Uploads

```python
async def run_upload_processor():
    manager = create_satellite_manager()
    
    # Iniciar procesador en background
    await manager.process_upload_queue()

# Ejecutar en loop infinito
asyncio.run(run_upload_processor())
```

### Obtener Estadísticas

```python
manager = create_satellite_manager()
stats = manager.get_statistics()

print(f"Total satélites: {stats['total_satellites']}")
print(f"Uploads totales: {stats['total_uploads']}")
print(f"Vistas totales: {stats['total_views']}")

for sat in stats['satellites']:
    print(f"  {sat['name']}: {sat['uploads']} uploads")
```

---

## 🎬 INTEGRACIÓN CON LONGCAT-VIDEO

### Workflow Completo

```python
from ml_core.video_generation import create_video_generator
from ml_core.satellite_manager import create_satellite_manager
import asyncio

async def create_and_upload_video():
    # 1. Generar video con LongCat
    video_gen = create_video_generator()
    await video_gen.initialize()
    
    result = await video_gen.generate_text_to_video(
        prompt="Urban artist in recording studio, trap vibes",
        duration=10,
        output_name="trap_session_001"
    )
    
    if result.success:
        # 2. Programar upload en satélite
        sat_manager = create_satellite_manager()
        
        task = await sat_manager.schedule_upload(
            video_path=result.video_path,
            audio_path="data/audio/my_track.mp3",
            niche="trap_spanish_latino"
        )
        
        print(f"✅ Video generado y programado: {task.scheduled_time}")

asyncio.run(create_and_upload_video())
```

---

## 📈 ESTRATEGIA DE CONTENIDO

### Distribución Automática

El sistema usa una estrategia inteligente para cada satélite:

**Satélite 1 (Trap):**
- 40% contenido nuevo
- 30% remixes
- 20% trending
- 10% experimental

**Satélite 2 (Urban):**
- 35% contenido nuevo
- 35% remixes
- 25% trending
- 5% experimental

**Satélite 3 (HipHop):**
- 50% contenido nuevo
- 20% remixes
- 20% trending
- 10% experimental

### Load Balancing

El sistema selecciona automáticamente el satélite menos utilizado para distribuir la carga:

```python
# Selección automática
satellite = manager.select_satellite_for_content(niche="trap_spanish_latino")
```

---

## 🔧 CONFIGURACIÓN AVANZADA

### Modificar Horarios de Upload

Edita `config/satellite_accounts_config.json`:

```json
{
  "upload_schedule": ["12:00", "18:00", "22:00"],
  "timezone": "Europe/Madrid"
}
```

### Cambiar Estrategia de Contenido

```json
{
  "content_strategy": {
    "new_content": 0.5,
    "remixes": 0.3,
    "trending": 0.15,
    "experimental": 0.05
  }
}
```

### Ajustar Frecuencia

```json
{
  "upload_frequency": 3,  // Cambiar a 4 para más uploads
  "upload_schedule": ["10:00", "14:00", "18:00", "22:00"]
}
```

---

## 🎯 PROYECCIONES Y MÉTRICAS

Ver archivo completo: `SATELLITE_ACCOUNTS_STATS.md`

**Resumen 30 días:**
- Videos generados: 360
- Vistas estimadas: 18K - 36K
- Suscriptores: 180 - 360
- ROI: 1,200% - 3,000%

**Proyección 1 año:**
- Videos: 4,320
- Vistas: 2M - 5M
- Suscriptores: 50K - 100K
- Ingresos: $2K - $5K/mes
- ROI anual: 8,000% - 20,000%

---

## 🚨 TROUBLESHOOTING

### Token Expirado

```bash
# Re-generar token para satélite específico
python configure_satellite_tokens.py
# Selecciona el satélite a actualizar
```

### Upload Fallido

```python
# Verificar estado de uploads
manager = create_satellite_manager()
failed_tasks = [t for t in manager.upload_queue if t.status == "failed"]

for task in failed_tasks:
    print(f"Failed: {task.satellite_id} - {task.video_path}")
```

### Canal Satélite Inactivo

```python
# Desactivar satélite temporalmente
satellite = manager.satellites["satellite_01"]
satellite.is_active = False

# Reactivar
satellite.is_active = True
```

---

## 📚 SCRIPTS ÚTILES

### Generar Tokens para Todos los Satélites

```bash
python configure_satellite_tokens.py
# Ingresa '0' para configurar todos
```

### Ver Estadísticas en Tiempo Real

```python
import time
from ml_core.satellite_manager import create_satellite_manager

manager = create_satellite_manager()

while True:
    stats = manager.get_statistics()
    print(f"\rUploads: {stats['total_uploads']} | Pending: {stats['pending_uploads']}", end="")
    time.sleep(10)
```

### Exportar Configuración

```python
import json
from ml_core.satellite_manager import create_satellite_manager

manager = create_satellite_manager()
stats = manager.get_statistics()

with open("satellite_stats.json", "w") as f:
    json.dump(stats, f, indent=2)
```

---

## 🎉 PRÓXIMOS PASOS

1. ✅ Configura tokens OAuth para cada satélite
2. ✅ Verifica que todos los satélites estén activos
3. 🚀 Integra con LongCat-Video para generación automática
4. 📊 Monitorea métricas y ajusta estrategia
5. 💰 Monetiza cuando alcances los requisitos de YouTube

---

**🛰️ Sistema de cuentas satélite listo para escalar tu presencia en YouTube 🚀**
