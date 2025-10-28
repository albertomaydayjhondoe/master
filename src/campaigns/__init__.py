"""
Campaigns Domain - Gestión de Campañas de Marketing
Dominio principal para la creación, optimización y gestión de campañas cross-platform
"""

from .domain import *
from .application import *

__version__ = "1.0.0"
__domain__ = "campaigns"
__description__ = "Campaign Management Domain with Cross-Platform Optimization"

__all__ = ["domain", "application", "infrastructure", "interfaces"]