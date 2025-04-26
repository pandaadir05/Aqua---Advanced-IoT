"""
Aqua - Next Generation IoT Security Scanner.
"""

__version__ = "1.0.0"
__author__ = "Adir"
__email__ = "adir@example.com"

from .cli import app
from .core import (
    BehavioralAnalyzer,
    ReportGenerator,
    AlertManager
)

__all__ = [
    "app",
    "BehavioralAnalyzer",
    "ReportGenerator",
    "AlertManager"
] 