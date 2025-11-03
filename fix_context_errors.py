#!/usr/bin/env python3
"""
Script para corregir errores de contexto del repositorio según buenas prácticas.
Enfocado en el sistema de automatización de Telegram y integración con otras ramas.
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContextFixer:
    """Clase para corregir errores de contexto del repositorio."""
    
    def __init__(self, repo_path: str = "/workspaces/master"):
        self.repo_path = Path(repo_path)
        self.errors_fixed = 0
        self.files_processed = 0
        
    def fix_type_annotations(self) -> None:
        """Corregir anotaciones de tipo faltantes."""
        logger.info("🔧 Corrigiendo anotaciones de tipo...")
        
        # Archivos con errores de tipo conocidos
        files_to_fix = [
            "ml_core/models/factory.py",
            "ml_core/models/yolo_coco_pretrained.py", 
            "test_coco_system.py",
            "test_coco_simple.py",
            "test_coco_real.py",
            "test_coco_api.py",
            "examples/coco_usage_examples.py",
            "gologin_automation/anonymity_context.py"
        ]
        
        for file_path in files_to_fix:
            full_path = self.repo_path / file_path
            if full_path.exists():
                self._fix_file_type_annotations(full_path)
                
    def _fix_file_type_annotations(self, file_path: Path) -> None:
        """Corregir anotaciones de tipo en un archivo específico."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Patrones comunes de corrección
            fixes = [
                # Funciones sin tipo de retorno
                ("def is_dummy_mode():", "def is_dummy_mode() -> bool:"),
                ("def get_env(var_name, default=None):", "def get_env(var_name: str, default: Optional[str] = None) -> Optional[str]:"),
                ("def _load_impl(env_var: str, default_callable):", "def _load_impl(env_var: str, default_callable: Any) -> Any:"),
                ("def _init_model(self):", "def _init_model(self) -> None:"),
                ("def _init_dummy_mode(self):", "def _init_dummy_mode(self) -> None:"),
                ("def _warmup_model(self):", "def _warmup_model(self) -> None:"),
                ("def __post_init__(self):", "def __post_init__(self) -> None:"),
                ("def mark_used(self):", "def mark_used(self) -> None:"),
                
                # Funciones de test
                ("def test_", "def test_"),  # Placeholder - se corrige individualmente
                ("def main():", "def main() -> None:"),
                ("def create_test_image():", "def create_test_image() -> bytes:"),
                ("def create_example_image():", "def create_example_image() -> bytes:"),
            ]
            
            # Aplicar correcciones generales
            modified = False
            for old, new in fixes:
                if old in content and old != new:
                    content = content.replace(old, new)
                    modified = True
            
            # Correcciones específicas para funciones de test
            if "def test_" in content:
                # Agregar tipo de retorno None a funciones de test
                import re
                pattern = r'def (test_\w+)\(([^)]*)\):'
                replacement = r'def \1(\2) -> None:'
                content = re.sub(pattern, replacement, content)
                modified = True
            
            # Correcciones de variables
            content = content.replace(
                "class_counts = {}",
                "class_counts: Dict[str, int] = {}"
            )
            
            # Agregar imports necesarios
            if "-> bool:" in content or "-> None:" in content or "-> Any:" in content:
                if "from typing import" not in content:
                    # Encontrar el lugar apropiado para insertar imports
                    lines = content.split('\n')
                    import_idx = 0
                    for i, line in enumerate(lines):
                        if line.startswith('import ') or line.startswith('from '):
                            import_idx = i + 1
                        elif line.strip() == "" and import_idx > 0:
                            break
                    
                    typing_import = "from typing import Dict, List, Optional, Any, Union"
                    if typing_import not in content:
                        lines.insert(import_idx, typing_import)
                        content = '\n'.join(lines)
                        modified = True
            
            if modified:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"✅ Corregido: {file_path}")
                self.errors_fixed += 1
            
            self.files_processed += 1
                
        except Exception as e:
            logger.error(f"❌ Error corrigiendo {file_path}: {e}")
    
    def fix_import_structure(self) -> None:
        """Corregir estructura de imports en telegram_automation."""
        logger.info("🔧 Corrigiendo estructura de imports...")
        
        telegram_path = self.repo_path / "telegram_automation"
        if not telegram_path.exists():
            return
        
        # Crear __init__.py files para hacer packages válidos
        init_files = [
            telegram_path / "__init__.py",
            telegram_path / "core" / "__init__.py",
            telegram_path / "config" / "__init__.py", 
            telegram_path / "integrations" / "__init__.py",
            telegram_path / "database" / "__init__.py"
        ]
        
        for init_file in init_files:
            if not init_file.exists():
                init_file.parent.mkdir(parents=True, exist_ok=True)
                with open(init_file, 'w') as f:
                    f.write('"""Package initialization."""\n')
                logger.info(f"✅ Creado: {init_file}")
                self.errors_fixed += 1
    
    def fix_requirements(self) -> None:
        """Corregir y consolidar archivos requirements."""
        logger.info("🔧 Corrigiendo archivos requirements...")
        
        # Crear requirements.txt principal para telegram_automation
        telegram_req_path = self.repo_path / "telegram_automation" / "requirements.txt"
        telegram_requirements = [
            "# Telegram Automation System Requirements",
            "telethon>=1.41.0",
            "fastapi>=0.120.0",
            "uvicorn>=0.38.0",
            "scikit-learn>=1.7.0",
            "aiohttp>=3.13.0",
            "requests>=2.32.0",
            "pydantic>=2.12.0",
            "python-multipart>=0.0.9",
            "asyncio-mqtt>=0.14.0",
            "cryptography>=42.0.0",
            "sqlalchemy>=2.0.0",
            "alembic>=1.13.0",
            "python-dotenv>=1.0.0",
            "Pillow>=10.0.0"
        ]
        
        with open(telegram_req_path, 'w') as f:
            f.write('\n'.join(telegram_requirements))
        logger.info(f"✅ Creado: {telegram_req_path}")
        
        # Actualizar requirements principal
        main_req_path = self.repo_path / "requirements.txt"
        if main_req_path.exists():
            with open(main_req_path, 'r') as f:
                current_reqs = f.read()
            
            # Agregar requirements de telegram si no están
            new_reqs = [
                "telethon>=1.41.0",
                "fastapi>=0.120.0", 
                "uvicorn>=0.38.0"
            ]
            
            for req in new_reqs:
                if req not in current_reqs:
                    current_reqs += f"\n{req}"
            
            with open(main_req_path, 'w') as f:
                f.write(current_reqs)
        
        self.errors_fixed += 1
    
    def fix_config_files(self) -> None:
        """Corregir archivos de configuración."""
        logger.info("🔧 Corrigiendo archivos de configuración...")
        
        # Crear .env.example para telegram_automation
        env_example_path = self.repo_path / "telegram_automation" / ".env.example"
        env_example_content = """# Telegram Bot Configuration
BOT_TOKEN=your_telegram_bot_token_here
API_ID=your_telegram_api_id
API_HASH=your_telegram_api_hash
PHONE_NUMBER=your_phone_number

# Platform API Keys
YOUTUBE_API_KEY=your_youtube_api_key
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password
TIKTOK_CLIENT_KEY=your_tiktok_client_key
TIKTOK_CLIENT_SECRET=your_tiktok_client_secret

# System Settings
DUMMY_MODE=true
LOG_LEVEL=INFO
MAX_CONCURRENT_TASKS=5

# Database
DATABASE_URL=sqlite:///telegram_automation.db

# Security
ENCRYPTION_KEY=change_in_production_32_chars_min

# Monitoring
ALERT_WEBHOOK_URL=https://your-webhook-url.com/alerts
"""
        
        with open(env_example_path, 'w') as f:
            f.write(env_example_content)
        logger.info(f"✅ Creado: {env_example_path}")
        
        # Crear docker-compose.yml para desarrollo
        docker_compose_path = self.repo_path / "telegram_automation" / "docker-compose.yml"
        docker_compose_content = """version: '3.8'

services:
  telegram-bot:
    build: .
    environment:
      - DUMMY_MODE=true
      - LOG_LEVEL=INFO
    volumes:
      - .:/app
      - ./data:/app/data
    ports:
      - "8000:8000"
    restart: unless-stopped
    
  postgres:
    image: postgres:13
    environment:
      - POSTGRES_DB=telegram_automation
      - POSTGRES_USER=telegram
      - POSTGRES_PASSWORD=telegram123
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

volumes:
  postgres_data:
"""
        
        with open(docker_compose_path, 'w') as f:
            f.write(docker_compose_content)
        logger.info(f"✅ Creado: {docker_compose_path}")
        
        self.errors_fixed += 2
    
    def create_dockerfile(self) -> None:
        """Crear Dockerfile para telegram_automation."""
        logger.info("🔧 Creando Dockerfile...")
        
        dockerfile_path = self.repo_path / "telegram_automation" / "Dockerfile"
        dockerfile_content = """FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 telegram && chown -R telegram:telegram /app
USER telegram

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["python", "main_bot.py"]
"""
        
        with open(dockerfile_path, 'w') as f:
            f.write(dockerfile_content)
        logger.info(f"✅ Creado: {dockerfile_path}")
        self.errors_fixed += 1
    
    def create_makefile(self) -> None:
        """Crear Makefile para comandos comunes."""
        logger.info("🔧 Creando Makefile...")
        
        makefile_path = self.repo_path / "telegram_automation" / "Makefile"
        makefile_content = """.PHONY: install test run clean docker-build docker-run

# Install requirements
install:
	pip install -r requirements.txt

# Run tests
test:
	python simple_test.py

# Run integration tests
test-integration:
	python test_integration.py

# Run the bot
run:
	python main_bot.py

# Run API server
api:
	python api_gateway.py

# Clean cache files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +

# Docker build
docker-build:
	docker-compose build

# Docker run
docker-run:
	docker-compose up -d

# Docker logs
docker-logs:
	docker-compose logs -f

# Docker stop
docker-stop:
	docker-compose down

# Setup development environment
setup-dev:
	cp .env.example .env
	pip install -r requirements.txt
	python -c "from database.models import create_tables; create_tables()"

# Format code
format:
	black . --line-length 88
	isort . --profile black

# Lint code
lint:
	flake8 . --max-line-length=88 --extend-ignore=E203,W503
	mypy . --ignore-missing-imports

# Full check
check: lint test

# Update requirements
update-reqs:
	pip-compile requirements.in
"""
        
        with open(makefile_path, 'w') as f:
            f.write(makefile_content)
        logger.info(f"✅ Creado: {makefile_path}")
        self.errors_fixed += 1
    
    def fix_gitignore(self) -> None:
        """Actualizar .gitignore con patrones apropiados."""
        logger.info("🔧 Actualizando .gitignore...")
        
        gitignore_path = self.repo_path / ".gitignore"
        additional_patterns = [
            "",
            "# Telegram Automation",
            "telegram_automation/.env",
            "telegram_automation/data/",
            "telegram_automation/*.db",
            "telegram_automation/*.session",
            "telegram_automation/logs/",
            "",
            "# ML Models",
            "*.pt",
            "*.onnx", 
            "data/models/",
            "",
            "# GoLogin",
            "gologin_profiles/",
            "browser_profiles/",
            "",
            "# API Keys and Secrets",
            "*.key",
            "*.pem",
            "secrets/",
            ""
        ]
        
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                current_content = f.read()
            
            # Solo agregar patrones que no existen
            new_patterns = []
            for pattern in additional_patterns:
                if pattern not in current_content:
                    new_patterns.append(pattern)
            
            if new_patterns:
                with open(gitignore_path, 'a') as f:
                    f.write('\n'.join(new_patterns))
                logger.info(f"✅ Actualizado: {gitignore_path}")
                self.errors_fixed += 1
    
    def create_documentation(self) -> None:
        """Crear documentación adicional."""
        logger.info("🔧 Creando documentación...")
        
        # Guía de contribución
        contributing_path = self.repo_path / "CONTRIBUTING.md"
        contributing_content = """# Contributing to TikTok Viral ML System

## Development Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd master
```

2. **Set up the environment**
```bash
# For Telegram automation
cd telegram_automation
make setup-dev
```

3. **Run tests**
```bash
make test
```

## Branch Structure

- `main` - Production ready code
- `tele` - Telegram automation system
- `rama` - TikTok ML components
- `meta` - Meta advertising automation

## Coding Standards

- Use type hints for all functions
- Follow PEP 8 style guidelines
- Write comprehensive tests
- Document all public APIs
- Use meaningful commit messages

## Testing

- Unit tests for individual components
- Integration tests for system workflows  
- End-to-end tests for complete scenarios
- All tests must pass before merging

## Security

- Never commit API keys or secrets
- Use environment variables for configuration
- Implement proper input validation
- Follow security best practices
"""
        
        with open(contributing_path, 'w') as f:
            f.write(contributing_content)
        logger.info(f"✅ Creado: {contributing_path}")
        
        # Changelog template
        changelog_path = self.repo_path / "telegram_automation" / "CHANGELOG.md"
        changelog_content = """# Changelog

All notable changes to the Telegram Automation System will be documented in this file.

## [Unreleased]

### Added
- Complete 6-module Telegram automation system
- ML-based priority calculation engine
- Cross-platform engagement automation (YouTube, Instagram, TikTok)
- Viral content detection and monitoring
- Dynamic message generation with personalization
- Multi-account management with health monitoring
- REST API for external integration
- Comprehensive testing framework

### Changed
- Improved type annotations across all modules
- Enhanced error handling and logging
- Optimized performance for concurrent operations

### Fixed
- Import structure and dependencies
- Configuration management
- Database model definitions

## [1.0.0] - 2024-11-02

### Added
- Initial release of Telegram automation system
- Core modules: Listener, Executor, Priority Engine, Metrics, Messages, Accounts
- Platform integrations for YouTube, Instagram, TikTok
- Complete dummy mode for safe development
- Production-ready architecture
"""
        
        with open(changelog_path, 'w') as f:
            f.write(changelog_content)
        logger.info(f"✅ Creado: {changelog_path}")
        
        self.errors_fixed += 2
    
    def run_all_fixes(self) -> None:
        """Ejecutar todas las correcciones."""
        logger.info("🚀 Iniciando correcciones de contexto del repositorio...")
        logger.info("=" * 60)
        
        fixes = [
            ("Anotaciones de tipo", self.fix_type_annotations),
            ("Estructura de imports", self.fix_import_structure), 
            ("Archivos requirements", self.fix_requirements),
            ("Archivos de configuración", self.fix_config_files),
            ("Dockerfile", self.create_dockerfile),
            ("Makefile", self.create_makefile),
            ("GitIgnore", self.fix_gitignore),
            ("Documentación", self.create_documentation)
        ]
        
        for fix_name, fix_func in fixes:
            try:
                logger.info(f"\n🔧 Aplicando: {fix_name}")
                fix_func()
                logger.info(f"✅ Completado: {fix_name}")
            except Exception as e:
                logger.error(f"❌ Error en {fix_name}: {e}")
        
        logger.info(f"\n🎯 Resumen de correcciones:")
        logger.info(f"   📁 Archivos procesados: {self.files_processed}")
        logger.info(f"   🔧 Errores corregidos: {self.errors_fixed}")
        logger.info(f"   ✅ Sistema optimizado para el propósito definido")

def main() -> None:
    """Función principal."""
    print("🚀 Corrector de contexto del repositorio")
    print("Optimizando para sistema de automatización de Telegram")
    print("=" * 60)
    
    fixer = ContextFixer()
    fixer.run_all_fixes()
    
    print("\n🎉 Correcciones completadas!")
    print("El repositorio está optimizado según buenas prácticas.")

if __name__ == "__main__":
    main()