"""
Core package for Aqua.
"""

from .device import IoTDevice, DeviceType, Protocol  
from .vulnerability import Vulnerability, Severity, VulnerabilityType
from .behavioral import BehavioralAnalyzer
from .reporting import ReportGenerator
from .alerting import AlertManager, AlertType, AlertSeverity
from .framework import IoTPTF
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
    "IoTPTF",
    "ProtectionEngine"
]
