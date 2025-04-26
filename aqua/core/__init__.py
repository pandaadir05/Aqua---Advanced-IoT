"""
Core package for Aqua.
"""

from .device import IoTDevice, DeviceType, Protocol  
from .vulnerability import Vulnerability, Severity, VulnerabilityType
from .behavioral import BehavioralAnalyzer
from .reporting import ReportGenerator
from .alerting import AlertManager, AlertType, AlertSeverity
from .framework import Aqua, IoTPTF  # Include both for backward compatibility
from .protection import ProtectionEngine

__all__ = [
    "IoTDevice",
    "DeviceType", 
    "Protocol",
    "Vulnerability",
    "Severity",
    "VulnerabilityType",
    "BehavioralAnalyzer",
    "ReportGenerator",
    "AlertManager", 
    "AlertType",
    "AlertSeverity",
    "Aqua",  # Add the new class name
    "IoTPTF",  # Keep for backward compatibility
    "ProtectionEngine"
]
