"""
Alerting System for Aqua.
"""

from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime
from loguru import logger

class AlertSeverity(Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class AlertType(Enum):
    NETWORK = "NETWORK"
    PROCESS = "PROCESS"
    FILE = "FILE"
    BEHAVIORAL = "BEHAVIORAL"
    SYSTEM = "SYSTEM"

class AlertManager:
    """Alert management system with notification channels."""
    
    def __init__(self):
        self.alert_history = []
        
    def create_alert(self, 
                    alert_type: AlertType,
                    severity: AlertSeverity,
                    message: str,
                    details: Dict = None) -> Dict:
        """Create a new alert."""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "type": alert_type.value,
            "severity": severity.value,
            "message": message,
            "details": details or {},
            "status": "NEW"
        }
        
        self.alert_history.append(alert)
        logger.warning(f"ALERT: [{alert['severity']}] {alert['message']}")
        return alert
        
    def get_alert_history(self, limit: int = 100) -> List[Dict]:
        """Get filtered alert history."""
        return self.alert_history[-limit:]
        
    def clear_alert_history(self):
        """Clear alert history."""
        self.alert_history = []