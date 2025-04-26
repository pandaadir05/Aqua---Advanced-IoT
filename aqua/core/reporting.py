"""
Reporting and Analytics Module for Aqua.
"""

import json
from datetime import datetime
from pathlib import Path
import logging
from loguru import logger
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import threading
import time
from collections import defaultdict

from aqua.core.alerting import AlertManager, AlertType, AlertSeverity

console = Console()

class ReportGenerator:
    """Advanced reporting and analytics system."""
    
    def __init__(self):
        self.config_path = Path("config/reporting.json")
        self.config_path.parent.mkdir(exist_ok=True)
        self.load_config()
        
        # Initialize data storage
        self.network_stats = defaultdict(list)
        self.process_stats = defaultdict(list)
        self.file_stats = defaultdict(list)
        self.alert_history = []
        
        # Initialize alert manager
        self.alert_manager = AlertManager()
        
        # Start background data collection
        self.collection_thread = threading.Thread(target=self._background_collection)
        self.collection_thread.daemon = True
        self.collection_thread.start()
        
    def load_config(self):
        """Load reporting configuration."""
        if self.config_path.exists():
            with open(self.config_path) as f:
                self.config = json.load(f)
        else:
            self.config = {
                "report_types": {
                    "daily": True,
                    "weekly": True,
                    "monthly": True
                },
                "metrics": {
                    "network": {
                        "traffic_volume": True,
                        "connection_attempts": True,
                        "port_scan_activity": True,
                        "protocol_distribution": True
                    },
                    "process": {
                        "cpu_usage": True,
                        "memory_usage": True,
                        "io_operations": True,
                        "network_connections": True
                    },
                    "file": {
                        "access_patterns": True,
                        "modification_rate": True,
                        "permission_changes": True
                    }
                },
                "visualization": {
                    "charts": True,
                    "tables": True,
                    "trends": True
                },
                "export_formats": {
                    "json": True,
                    "csv": True,
                    "pdf": True
                },
                "retention_period": 30  # days
            }
            self.save_config()
            
    def save_config(self):
        """Save reporting configuration."""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
            
    def add_network_stat(self, stat_type: str, value: float):
        """Add network statistic."""
        self.network_stats[stat_type].append({
            "value": value,
            "timestamp": datetime.now().isoformat()
        })
        
    def add_process_stat(self, stat_type: str, value: float):
        """Add process statistic."""
        self.process_stats[stat_type].append({
            "value": value,
            "timestamp": datetime.now().isoformat()
        })
        
    def add_file_stat(self, stat_type: str, value: float):
        """Add file statistic."""
        self.file_stats[stat_type].append({
            "value": value,
            "timestamp": datetime.now().isoformat()
        })
        
    def add_alert(self, alert: Dict):
        """Add alert to history."""
        self.alert_history.append({
            **alert,
            "timestamp": datetime.now().isoformat()
        })
        
    def generate_report(self, report_type: str) -> Dict:
        """Generate comprehensive report."""
        try:
            report = {
                "metadata": {
                    "type": report_type,
                    "generated_at": datetime.now().isoformat(),
                    "time_range": self._get_time_range(report_type)
                },
                "network_analysis": self._analyze_network_data(),
                "process_analysis": self._analyze_process_data(),
                "file_analysis": self._analyze_file_data(),
                "alert_summary": self._analyze_alerts(),
                "recommendations": self._generate_recommendations()
            }
            
            # Export report
            self._export_report(report, report_type)
            
            return report
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return {}
            
    def _analyze_network_data(self) -> Dict:
        """Analyze network statistics."""
        analysis = {}
        
        for stat_type, data in self.network_stats.items():
            if self.config["metrics"]["network"].get(stat_type, False):
                values = [d["value"] for d in data]
                analysis[stat_type] = {
                    "mean": np.mean(values),
                    "std": np.std(values),
                    "max": np.max(values),
                    "min": np.min(values),
                    "trend": self._calculate_trend(values)
                }
                
        return analysis
        
    def _analyze_process_data(self) -> Dict:
        """Analyze process statistics."""
        analysis = {}
        
        for stat_type, data in self.process_stats.items():
            if self.config["metrics"]["process"].get(stat_type, False):
                values = [d["value"] for d in data]
                analysis[stat_type] = {
                    "mean": np.mean(values),
                    "std": np.std(values),
                    "max": np.max(values),
                    "min": np.min(values),
                    "trend": self._calculate_trend(values)
                }
                
        return analysis
        
    def _analyze_file_data(self) -> Dict:
        """Analyze file statistics."""
        analysis = {}
        
        for stat_type, data in self.file_stats.items():
            if self.config["metrics"]["file"].get(stat_type, False):
                values = [d["value"] for d in data]
                analysis[stat_type] = {
                    "mean": np.mean(values),
                    "std": np.std(values),
                    "max": np.max(values),
                    "min": np.min(values),
                    "trend": self._calculate_trend(values)
                }
                
        return analysis
        
    def _analyze_alerts(self) -> Dict:
        """Analyze alert history."""
        if not self.alert_history:
            return {}
            
        # Group alerts by type and severity
        alert_groups = defaultdict(lambda: defaultdict(int))
        for alert in self.alert_history:
            alert_groups[alert["type"]][alert["severity"]] += 1
            
        return {
            "total_alerts": len(self.alert_history),
            "alert_distribution": dict(alert_groups),
            "trend": self._calculate_alert_trend()
        }
        
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend from values."""
        if len(values) < 2:
            return "insufficient data"
            
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        if slope > 0.1:
            return "increasing"
        elif slope < -0.1:
            return "decreasing"
        else:
            return "stable"
            
    def _calculate_alert_trend(self) -> str:
        """Calculate alert trend."""
        if len(self.alert_history) < 2:
            return "insufficient data"
            
        # Count alerts per day
        daily_counts = defaultdict(int)
        for alert in self.alert_history:
            date = alert["timestamp"].split("T")[0]
            daily_counts[date] += 1
            
        values = list(daily_counts.values())
        return self._calculate_trend(values)
        
    def _get_time_range(self, report_type: str) -> Dict:
        """Get time range for report."""
        now = datetime.now()
        
        if report_type == "daily":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif report_type == "weekly":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            start = start - pd.Timedelta(days=now.weekday())
        elif report_type == "monthly":
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            start = now - pd.Timedelta(days=1)
            
        return {
            "start": start.isoformat(),
            "end": now.isoformat()
        }
        
    def _generate_recommendations(self) -> List[str]:
        """Generate security recommendations."""
        recommendations = []
        
        # Analyze network patterns
        network_analysis = self._analyze_network_data()
        if "port_scan_activity" in network_analysis:
            if network_analysis["port_scan_activity"]["mean"] > 100:
                recommendations.append("High port scan activity detected. Consider implementing stricter firewall rules.")
                
        # Analyze process patterns
        process_analysis = self._analyze_process_data()
        if "cpu_usage" in process_analysis:
            if process_analysis["cpu_usage"]["mean"] > 80:
                recommendations.append("High CPU usage detected. Investigate resource-intensive processes.")
                
        # Analyze file patterns
        file_analysis = self._analyze_file_data()
        if "permission_changes" in file_analysis:
            if file_analysis["permission_changes"]["mean"] > 10:
                recommendations.append("Frequent permission changes detected. Review file access policies.")
                
        return recommendations
        
    def _export_report(self, report: Dict, report_type: str):
        """Export report in configured formats."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_path = Path(f"reports/{report_type}_{timestamp}")
        base_path.parent.mkdir(exist_ok=True)
        
        if self.config["export_formats"]["json"]:
            with open(base_path.with_suffix(".json"), 'w') as f:
                json.dump(report, f, indent=2)
                
        if self.config["export_formats"]["csv"]:
            # Convert relevant data to DataFrame and save as CSV
            pass
            
        if self.config["export_formats"]["pdf"]:
            # Generate PDF report with visualizations
            pass
            
    def _background_collection(self):
        """Background thread for data collection."""
        while True:
            try:
                # Clean up old data
                self._cleanup_old_data()
                
                # Collect new data
                self._collect_network_data()
                self._collect_process_data()
                self._collect_file_data()
                
            except Exception as e:
                logger.error(f"Background data collection failed: {e}")
                
            time.sleep(300)  # 5 minutes
            
    def _cleanup_old_data(self):
        """Remove data older than retention period."""
        cutoff = datetime.now() - pd.Timedelta(days=self.config["retention_period"])
        
        for stats in [self.network_stats, self.process_stats, self.file_stats]:
            for stat_type in stats:
                stats[stat_type] = [
                    d for d in stats[stat_type]
                    if datetime.fromisoformat(d["timestamp"]) > cutoff
                ]
                
        self.alert_history = [
            alert for alert in self.alert_history
            if datetime.fromisoformat(alert["timestamp"]) > cutoff
        ]
        
    def _collect_network_data(self):
        """Collect network statistics."""
        # Implementation depends on specific network monitoring tools
        pass
        
    def _collect_process_data(self):
        """Collect process statistics."""
        # Implementation depends on specific process monitoring tools
        pass
        
    def _collect_file_data(self):
        """Collect file statistics."""
        # Implementation depends on specific file monitoring tools
        pass 