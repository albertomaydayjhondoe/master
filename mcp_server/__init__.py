"""
MCP Server - Model Context Protocol
Sistema de auto-reparación y manejo de dependencias
"""

import os
import logging

# Configurar logging MCP
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - MCP - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def initialize_mcp():
    """Inicializa sistema MCP"""
    try:
        from .mcp_auto_fix import MCPAutoFix
        
        logger.info("🔧 Iniciando sistema MCP...")
        auto_fix = MCPAutoFix()
        success = auto_fix.run_full_autofix()
        
        if success:
            logger.info("✅ Sistema MCP inicializado correctamente")
        else:
            logger.warning("⚠️ Sistema MCP inicializado con advertencias")
            
        return success
            
    except Exception as e:
        logger.error(f"❌ Error inicializando MCP: {e}")
        return False

# Auto-inicializar si está en modo desarrollo
if os.getenv("AUTO_INIT_MCP", "true").lower() == "true":
    initialize_mcp()

# Exportar componentes principales
try:
    from .mcp_error_handler import MCPServer, MCPDependencyManager, MCPErrorDetector
    from .mcp_auto_fix import MCPAutoFix, MCPSyntaxFixer, MCPImportFixer
    from .dummy_implementations import install_dummy_modules, get_dummy_implementation
    
    __all__ = [
        'MCPServer',
        'MCPDependencyManager', 
        'MCPErrorDetector',
        'MCPAutoFix',
        'MCPSyntaxFixer',
        'MCPImportFixer',
        'initialize_mcp',
        'install_dummy_modules',
        'get_dummy_implementation'
    ]
    
except ImportError as e:
    logger.warning(f"Algunos componentes MCP no pudieron importarse: {e}")
    __all__ = ['initialize_mcp']