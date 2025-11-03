# 📦 Gestión de Dependencias - TikTok Viral ML System

## 🎯 Resumen

Este sistema utiliza **requirements.txt específicos por rama** para optimizar las instalaciones y evitar conflictos de dependencias. Cada rama tiene sus propias necesidades:

- **RAMA MAIN** → `requirements-rama.txt` (ML completo + Device Farm)
- **RAMA META** → `requirements-meta.txt` (Meta Ads + GoLogin)  
- **RAMA TELE** → `requirements-tele.txt` (Telegram + Social)
- **DESARROLLO** → `requirements-dummy.txt` + `requirements-dev.txt`

## 🚀 Instalación Rápida

### Instalación Automática (Recomendado)
```bash
# El script detecta automáticamente tu rama
./install_dependencies.sh

# O especifica el modo manualmente
./install_dependencies.sh --rama    # RAMA MAIN
./install_dependencies.sh --meta    # RAMA META  
./install_dependencies.sh --tele    # RAMA TELE
./install_dependencies.sh --dummy   # Modo testing
```

### Instalación Manual
```bash
# 1. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# 2. Instalar dependencias base
pip install -r requirements.txt

# 3. Instalar dependencias específicas
pip install -r requirements-[rama|meta|tele].txt
```

## 📋 Descripción de Archivos

### `requirements.txt` (Base)
Dependencias **compartidas** por todas las ramas:
- FastAPI, SQLAlchemy, básicos de ML (numpy, pandas)
- Networking (httpx, aiohttp)
- Logging y utilidades

### `requirements-rama.txt` (RAMA MAIN)
**Sistema ML completo + Device Farm:**
- ✅ Ultralytics YOLOv8 + PyTorch
- ✅ Device automation (Appium, ADB)
- ✅ Módulo 7 completo (audio/video ML)
- ✅ Computer Vision avanzado
- 💾 **Espacio:** ~10GB (incluye modelos)
- 🔧 **GPU:** Recomendado

### `requirements-meta.txt` (RAMA META)
**Meta Ads + Browser Automation:**
- ✅ Facebook Business API
- ✅ Selenium + Playwright + GoLogin
- ✅ Proxy management + CAPTCHA solving
- ✅ Módulo 7 (audio/video básico)
- 💾 **Espacio:** ~2GB
- 🔧 **Extras:** Proxies, GoLogin setup

### `requirements-tele.txt` (RAMA TELE)
**Telegram Like4Like + Social:**
- ✅ Telegram APIs (Telethon, Pyrogram)
- ✅ Social media automation
- ✅ Módulo 7 completo (sincronización)
- ✅ Audio processing
- 💾 **Espacio:** ~3GB
- 🔧 **Extras:** Telegram API credentials

### `requirements-dummy.txt` (Testing)
**Modo desarrollo sin dependencias pesadas:**
- ✅ FastAPI + testing básico
- ✅ Sin PyTorch, sin APIs externas
- ✅ Mock data para todas las operaciones
- 💾 **Espacio:** ~500MB
- ⚡ **Instalación:** <5 minutos

### `requirements-dev.txt` (Desarrollo)
**Herramientas de desarrollo:**
- ✅ pytest, black, mypy
- ✅ Jupyter notebooks
- ✅ Pre-commit hooks

## 🔧 Uso por Ramas

### RAMA MAIN (TikTok ML + Device Farm)
```bash
git checkout main
./install_dependencies.sh --rama

# Verificación
python -c "import ultralytics; print('YOLOv8 OK')"
adb devices  # Verificar dispositivos conectados
```

**Características:**
- 🤖 YOLOv8 para análisis de video
- 📱 Automatización de 10 dispositivos Android
- 🎵 Módulo 7 completo (audio + video sync)
- 📊 ML pipeline completo

### RAMA META (Meta Ads + GoLogin)
```bash
git checkout meta
./install_dependencies.sh --meta

# Verificación
python -c "from facebook_business.api import FacebookAdsApi; print('Meta API OK')"
```

**Características:**
- 📊 Facebook Business API
- 🌐 GoLogin browser profiles
- 🔄 Proxy rotation + CAPTCHA solving
- 🎬 Módulo 7 para generación de ads

### RAMA TELE (Telegram Like4Like)
```bash
git checkout tele
./install_dependencies.sh --tele

# Verificación  
python -c "import telethon; print('Telegram OK')"
```

**Características:**
- 💬 Telegram Like4Like network
- 🔄 Social media cross-posting
- 🎵 Módulo 7 para contenido viral
- 📈 Analytics de engagement

## 🧪 Modo Dummy (Testing)

Perfect para **desarrollo**, **CI/CD** y **testing**:

```bash
./install_dependencies.sh --dummy
export DUMMY_MODE=true
uvicorn ml_core.api.main:app --reload
```

**Ventajas del Dummy Mode:**
- ⚡ Instalación súper rápida
- 🚫 Sin dependencias pesadas (PyTorch, etc.)
- 🎭 Datos simulados realistas
- ✅ Perfecto para testing de arquitectura
- 🔄 CI/CD friendly

## 🛠️ Troubleshooting

### Error: "No module named 'torch'"
```bash
# Si estás en RAMA MAIN, instala dependencias correctas
./install_dependencies.sh --rama
```

### Error: "Facebook Business API not found"
```bash
# Si estás en RAMA META, verifica instalación
pip install -r requirements-meta.txt
```

### Error: "ffmpeg not found"
```bash
# Instalar FFmpeg (sistema)
# Ubuntu/Debian:
sudo apt install ffmpeg

# macOS:
brew install ffmpeg

# Windows:
# Descargar desde https://ffmpeg.org/
```

### Conflictos de Dependencias
```bash
# Limpiar entorno y reinstalar
rm -rf venv
./install_dependencies.sh
```

### GPU no detectado (RAMA MAIN)
```bash
# Verificar CUDA
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"

# Reinstalar PyTorch con CUDA
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

## 📈 Optimización de Performance

### Instalación Selectiva
Si solo necesitas ciertos módulos, puedes instalar selectivamente:

```bash
# Solo ML básico (sin Device Farm)
pip install -r requirements.txt
pip install ultralytics torch torchvision

# Solo Meta Ads (sin GoLogin)
pip install -r requirements.txt  
pip install facebook-business requests

# Solo Telegram (sin audio processing)
pip install -r requirements.txt
pip install telethon python-telegram-bot
```

### Optimización de Espacio
```bash
# Limpiar cache de pip
pip cache purge

# Instalar sin cache (en producción)
pip install --no-cache-dir -r requirements-rama.txt

# Desinstalar paquetes no necesarios
pip uninstall <package> -y
```

## 🔄 Actualización de Dependencias

### Actualizar Todas las Dependencias
```bash
# Backup del entorno actual
pip freeze > current_requirements.txt

# Actualizar
pip install --upgrade -r requirements-rama.txt

# Si hay problemas, rollback
pip install -r current_requirements.txt
```

### Actualizar Solo Ciertas Librerías
```bash
# Actualizar Ultralytics
pip install --upgrade ultralytics

# Actualizar FastAPI
pip install --upgrade fastapi uvicorn
```

## 📊 Monitoreo de Dependencias

### Verificar Estado de Dependencias
```bash
# Check vulnerabilidades de seguridad
pip audit

# Ver dependencias obsoletas
pip list --outdated

# Árbol de dependencias
pip show <package>
```

### Requirements Lock Files
Para producción, considera usar **pipenv** o **poetry** para lock files:

```bash
# Con pipenv
pipenv install -r requirements-rama.txt
pipenv lock

# Con poetry  
poetry add $(cat requirements-rama.txt)
poetry lock
```

## 📚 Documentación Adicional

- 📖 [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) - Guía completa de desarrollo
- 🏗️ [BRANCH_STRUCTURE.md](BRANCH_STRUCTURE.md) - Arquitectura por ramas
- 🐳 [docker/](docker/) - Contenedores con dependencias preinstaladas
- 🧪 [tests/](tests/) - Tests para validar instalaciones

## 🚨 Notas Importantes

1. **Python 3.9-3.11 requerido** - Versiones más nuevas pueden tener incompatibilidades
2. **Espacio en disco** - RAMA MAIN requiere ~10GB para modelos ML
3. **GPU opcional** - Pero **altamente recomendado** para RAMA MAIN
4. **Dependencias de sistema** - FFmpeg, drivers de audio, etc.
5. **APIs externas** - Cada rama requiere diferentes tokens/keys

---

📧 **Soporte:** Si tienes problemas con dependencias, abre un issue con:
- Rama actual (`git branch`)
- Python version (`python --version`)
- SO y arquitectura
- Error completo + logs