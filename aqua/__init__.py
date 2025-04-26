"""
Aqua - Next Generation IoT Security Scanner.
"""

# Aqua IoT Security Platform package

__version__ = "1.0.0"
__author__ = "Adir"
__email__ = "adir@example.com"

try:
    from .cli import app
except ImportError:
    # This allows the package to be imported even if cli is not available
    pass

# Make web.app available for direct import
try:
    from .web.app import app as web_app
    from .web.auth import create_demo_user
    
    # Create demo user for easier testing
    create_demo_user()
except ImportError:
    # Web app might not be available
    pass

from .core import (
    BehavioralAnalyzer,
    ReportGenerator,
    AlertManager,
    IoTPTF
)

__all__ = [
    "app",
    "BehavioralAnalyzer",
    "ReportGenerator",
    "AlertManager",
    "IoTPTF",
    "web_app"
]