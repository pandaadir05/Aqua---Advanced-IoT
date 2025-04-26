"""
Enhanced Alerting System for Aqua.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import json
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
from pathlib import Path
import logging
from loguru import logger
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

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
    """Enhanced alert management system with multiple notification channels."""
    
    def __init__(self):
        self.config_path = Path("config/alerting.json")
        self.config_path.parent.mkdir(exist_ok=True)
        self.load_config()
        self.alert_history = []
        
    def load_config(self):
        """Load alerting configuration."""
        if self.config_path.exists():
            with open(self.config_path) as f:
                self.config = json.load(f)
        else:
            self.config = {
                "email": {
                    "enabled": False,
                    "smtp_server": "",
                    "smtp_port": 587,
                    "username": "",
                    "password": "",
                    "from_address": "",
                    "to_addresses": []
                },
                "siem": {
                    "enabled": False,
                    "endpoint": "",
                    "api_key": "",
                    "format": "CEF"  # Common Event Format
                },
                "webhook": {
                    "enabled": False,
                    "url": "",
                    "headers": {}
                },
                "severity_thresholds": {
                    "LOW": 1,
                    "MEDIUM": 5,
                    "HIGH": 10,
                    "CRITICAL": 20
                },
                "alert_rules": {
                    "network": {
                        "rate_limit": 1000,
                        "port_scan_threshold": 10,
                        "connection_threshold": 100
                    },
                    "process": {
                        "cpu_threshold": 80,
                        "memory_threshold": 80,
                        "unauthorized_processes": []
                    },
                    "file": {
                        "sensitive_paths": ["/etc", "/bin", "/sbin"],
                        "change_threshold": 5
                    }
                }
            }
            self.save_config()
            
    def save_config(self):
        """Save alerting configuration."""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
            
    def create_alert(self, 
                    alert_type: AlertType,
                    severity: AlertSeverity,
                    message: str,
                    details: Dict,
                    source: str = "Aqua") -> Dict:
        """Create a new alert with enhanced metadata."""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "type": alert_type.value,
            "severity": severity.value,
            "message": message,
            "details": details,
            "source": source,
            "status": "NEW"
        }
        
        self.alert_history.append(alert)
        self.notify(alert)
        return alert
        
    def notify(self, alert: Dict):
        """Send notifications through configured channels."""
        if self.config["email"]["enabled"]:
            self.send_email(alert)
            
        if self.config["siem"]["enabled"]:
            self.send_to_siem(alert)
            
        if self.config["webhook"]["enabled"]:
            self.send_webhook(alert)
            
        self.display_alert(alert)
        
    def send_email(self, alert: Dict):
        """Send alert via email."""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config["email"]["from_address"]
            msg['To'] = ', '.join(self.config["email"]["to_addresses"])
            msg['Subject'] = f"[{alert['severity']}] {alert['type']} Alert from {alert['source']}"
            
            body = f"""
            Alert Details:
            Type: {alert['type']}
            Severity: {alert['severity']}
            Time: {alert['timestamp']}
            Message: {alert['message']}
            
            Details:
            {json.dumps(alert['details'], indent=2)}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(self.config["email"]["smtp_server"], 
                            self.config["email"]["smtp_port"]) as server:
                server.starttls()
                server.login(self.config["email"]["username"], 
                           self.config["email"]["password"])
                server.send_message(msg)
                
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            
    def send_to_siem(self, alert: Dict):
        """Send alert to SIEM system."""
        try:
            headers = {
                "Authorization": f"Bearer {self.config['siem']['api_key']}",
                "Content-Type": "application/json"
            }
            
            # Convert to CEF format if configured
            if self.config["siem"]["format"] == "CEF":
                cef_data = self._convert_to_cef(alert)
                response = requests.post(
                    self.config["siem"]["endpoint"],
                    data=cef_data,
                    headers=headers
                )
            else:
                response = requests.post(
                    self.config["siem"]["endpoint"],
                    json=alert,
                    headers=headers
                )
                
            if response.status_code != 200:
                logger.error(f"Failed to send alert to SIEM: {response.text}")
                
        except Exception as e:
            logger.error(f"Failed to send alert to SIEM: {e}")
            
    def send_webhook(self, alert: Dict):
        """Send alert via webhook."""
        try:
            response = requests.post(
                self.config["webhook"]["url"],
                json=alert,
                headers=self.config["webhook"]["headers"]
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to send webhook alert: {response.text}")
                
        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")
            
    def display_alert(self, alert: Dict):
        """Display alert in console with enhanced formatting."""
        table = Table(show_header=True, header_style="bold red")
        table.add_column("Time", style="cyan")
        table.add_column("Type", style="yellow")
        table.add_column("Severity", style="red")
        table.add_column("Message", style="green")
        table.add_column("Details", style="blue")
        
        severity_color = {
            "INFO": "blue",
            "LOW": "green",
            "MEDIUM": "yellow",
            "HIGH": "red",
            "CRITICAL": "bold red"
        }
        
        table.add_row(
            alert["timestamp"],
            alert["type"],
            f"[{severity_color[alert['severity']]}]{alert['severity']}[/]",
            alert["message"],
            str(alert["details"])
        )
        
        console.print("\n[bold red]SECURITY ALERT[/bold red]")
        console.print(table)
        
    def _convert_to_cef(self, alert: Dict) -> str:
        """Convert alert to Common Event Format (CEF)."""
        # CEF:Version|Device Vendor|Device Product|Device Version|Signature ID|Name|Severity|Extension
        cef_version = "CEF:0"
        device_vendor = "Aqua"
        device_product = "Security Framework"
        device_version = "1.0"
        signature_id = f"AQUA-{alert['type']}-{alert['severity']}"
        name = alert["message"]
        severity = {
            "INFO": "1",
            "LOW": "3",
            "MEDIUM": "5",
            "HIGH": "7",
            "CRITICAL": "10"
        }.get(alert["severity"], "1")
        
        # Convert details to CEF extension format
        extension = []
        for key, value in alert["details"].items():
            extension.append(f"{key}={value}")
            
        return f"{cef_version}|{device_vendor}|{device_product}|{device_version}|{signature_id}|{name}|{severity}|{' '.join(extension)}"
        
    def get_alert_history(self, 
                         severity: Optional[AlertSeverity] = None,
                         alert_type: Optional[AlertType] = None,
                         limit: int = 100) -> List[Dict]:
        """Get filtered alert history."""
        filtered = self.alert_history
        
        if severity:
            filtered = [a for a in filtered if a["severity"] == severity.value]
            
        if alert_type:
            filtered = [a for a in filtered if a["type"] == alert_type.value]
            
        return filtered[-limit:]
        
    def clear_alert_history(self):
        """Clear alert history."""
        self.alert_history = [] 