"""
Advanced Protection Module for Aqua.
"""

import os
import sys
import json
import logging
from typing import Dict, List, Optional
from pathlib import Path
import psutil
import socket
import threading
import time
from datetime import datetime
import requests
from loguru import logger
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

class ProtectionEngine:
    """Advanced protection engine for IoT devices."""
    
    def __init__(self):
        self.config_path = Path("config/protection.json")
        self.config_path.parent.mkdir(exist_ok=True)
        self.load_config()
        self.active_protections = {}
        self.alert_history = []
        
    def load_config(self):
        """Load protection configuration."""
        if self.config_path.exists():
            with open(self.config_path) as f:
                self.config = json.load(f)
        else:
            self.config = {
                "network_protection": {
                    "enabled": True,
                    "block_ports": [22, 23, 80, 443],
                    "rate_limit": 100,
                    "whitelist": []
                },
                "process_protection": {
                    "enabled": True,
                    "monitor_processes": True,
                    "block_unauthorized": True
                },
                "file_protection": {
                    "enabled": True,
                    "monitor_paths": ["/etc", "/bin", "/sbin"],
                    "block_unauthorized": True
                },
                "alerting": {
                    "enabled": True,
                    "email_alerts": False,
                    "webhook_url": None
                }
            }
            self.save_config()
            
    def save_config(self):
        """Save protection configuration."""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
            
    def start_protection(self):
        """Start all protection mechanisms."""
        if self.config["network_protection"]["enabled"]:
            self.start_network_protection()
            
        if self.config["process_protection"]["enabled"]:
            self.start_process_protection()
            
        if self.config["file_protection"]["enabled"]:
            self.start_file_protection()
            
        logger.info("All protection mechanisms started")
        
    def start_network_protection(self):
        """Start network protection mechanisms."""
        def monitor_network():
            while True:
                try:
                    # Monitor network connections
                    connections = psutil.net_connections()
                    for conn in connections:
                        if conn.status == 'LISTEN':
                            port = conn.laddr.port
                            if port in self.config["network_protection"]["block_ports"]:
                                self.handle_unauthorized_port(port)
                                
                    # Monitor network traffic
                    net_io = psutil.net_io_counters()
                    if net_io.packets_recv > self.config["network_protection"]["rate_limit"]:
                        self.handle_high_traffic(net_io.packets_recv)
                        
                except Exception as e:
                    logger.error(f"Network monitoring error: {e}")
                    
                time.sleep(1)
                
        thread = threading.Thread(target=monitor_network, daemon=True)
        thread.start()
        self.active_protections["network"] = thread
        
    def start_process_protection(self):
        """Start process protection mechanisms."""
        def monitor_processes():
            while True:
                try:
                    for proc in psutil.process_iter(['pid', 'name', 'username']):
                        try:
                            if self.is_unauthorized_process(proc.info):
                                self.handle_unauthorized_process(proc.info)
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                except Exception as e:
                    logger.error(f"Process monitoring error: {e}")
                    
                time.sleep(5)
                
        thread = threading.Thread(target=monitor_processes, daemon=True)
        thread.start()
        self.active_protections["process"] = thread
        
    def start_file_protection(self):
        """Start file system protection mechanisms."""
        def monitor_files():
            while True:
                try:
                    for path in self.config["file_protection"]["monitor_paths"]:
                        path = Path(path)
                        if path.exists():
                            for file in path.rglob("*"):
                                if self.is_unauthorized_file(file):
                                    self.handle_unauthorized_file(file)
                except Exception as e:
                    logger.error(f"File monitoring error: {e}")
                    
                time.sleep(10)
                
        thread = threading.Thread(target=monitor_files, daemon=True)
        thread.start()
        self.active_protections["file"] = thread
        
    def is_unauthorized_process(self, proc_info: Dict) -> bool:
        """Check if a process is unauthorized."""
        # Add your process authorization logic here
        return False
        
    def is_unauthorized_file(self, file_path: Path) -> bool:
        """Check if a file is unauthorized."""
        # Add your file authorization logic here
        return False
        
    def handle_unauthorized_port(self, port: int):
        """Handle unauthorized port access."""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "type": "unauthorized_port",
            "port": port,
            "action": "blocked"
        }
        self.alert(alert)
        
    def handle_high_traffic(self, packet_count: int):
        """Handle high network traffic."""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "type": "high_traffic",
            "packet_count": packet_count,
            "action": "rate_limited"
        }
        self.alert(alert)
        
    def handle_unauthorized_process(self, proc_info: Dict):
        """Handle unauthorized process."""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "type": "unauthorized_process",
            "process": proc_info,
            "action": "terminated"
        }
        self.alert(alert)
        
    def handle_unauthorized_file(self, file_path: Path):
        """Handle unauthorized file access."""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "type": "unauthorized_file",
            "file": str(file_path),
            "action": "blocked"
        }
        self.alert(alert)
        
    def alert(self, alert_data: Dict):
        """Handle security alerts."""
        self.alert_history.append(alert_data)
        
        if self.config["alerting"]["enabled"]:
            # Display alert in console
            self.display_alert(alert_data)
            
            # Send webhook alert if configured
            if self.config["alerting"]["webhook_url"]:
                try:
                    requests.post(
                        self.config["alerting"]["webhook_url"],
                        json=alert_data
                    )
                except Exception as e:
                    logger.error(f"Failed to send webhook alert: {e}")
                    
    def display_alert(self, alert_data: Dict):
        """Display alert in console."""
        table = Table(show_header=True, header_style="bold red")
        table.add_column("Time", style="cyan")
        table.add_column("Type", style="yellow")
        table.add_column("Details", style="green")
        table.add_column("Action", style="red")
        
        table.add_row(
            alert_data["timestamp"],
            alert_data["type"],
            str(alert_data.get("port", alert_data.get("process", alert_data.get("file", "")))),
            alert_data["action"]
        )
        
        console.print("\n[bold red]SECURITY ALERT[/bold red]")
        console.print(table)
        
    def get_status(self) -> Dict:
        """Get protection status."""
        return {
            "active_protections": list(self.active_protections.keys()),
            "alert_count": len(self.alert_history),
            "config": self.config
        }
        
    def stop_protection(self):
        """Stop all protection mechanisms."""
        for thread in self.active_protections.values():
            thread.join(timeout=1)
        self.active_protections.clear()
        logger.info("All protection mechanisms stopped") 