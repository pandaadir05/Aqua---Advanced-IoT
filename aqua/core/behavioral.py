"""
Behavioral Analysis and Machine Learning Module for Aqua.
"""

import numpy as np
from typing import Dict, List, Optional
import json
from datetime import datetime
from pathlib import Path
import logging
from loguru import logger
from rich.console import Console
from rich.table import Table

console = Console()

class BehavioralAnalyzer:
    """Advanced behavioral analysis with machine learning capabilities."""
    
    def __init__(self):
        self.config_path = Path("config/behavioral.json")
        self.config_path.parent.mkdir(exist_ok=True, parents=True)
        self.load_config()
        
        # Initialize data storage
        self.network_data = []
        self.process_data = []
        self.file_data = []
        
    def load_config(self):
        """Load behavioral analysis configuration."""
        if self.config_path.exists():
            with open(self.config_path) as f:
                self.config = json.load(f)
        else:
            self.config = {
                "network_features": {
                    "packet_rate": True,
                    "connection_rate": True,
                    "port_scan_rate": True,
                    "traffic_volume": True,
                    "protocol_distribution": True
                },
                "process_features": {
                    "cpu_usage": True,
                    "memory_usage": True,
                    "io_operations": True,
                    "network_connections": True,
                    "file_access": True
                },
                "file_features": {
                    "access_patterns": True,
                    "modification_rate": True,
                    "size_changes": True,
                    "permission_changes": True
                },
                "training_interval": 3600,  # 1 hour
                "anomaly_threshold": 0.7
            }
            self.save_config()
            
    def save_config(self):
        """Save behavioral analysis configuration."""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
            
    def analyze_network_behavior(self, data: Dict) -> float:
        """Analyze network behavior using ML model."""
        try:
            # Extract features
            features = self._extract_network_features(data)
            
            # Store data for training
            self.network_data.append(features)
            
            # For now, we'll return a placeholder score
            # In a real implementation, we would use the ML model here
            return 0.5
            
        except Exception as e:
            logger.error(f"Network behavior analysis failed: {e}")
            return 0.0
            
    def analyze_process_behavior(self, data: Dict) -> float:
        """Analyze process behavior using ML model."""
        try:
            # Extract features
            features = self._extract_process_features(data)
            
            # Store data for training
            self.process_data.append(features)
            
            # For now, we'll return a placeholder score
            return 0.5
            
        except Exception as e:
            logger.error(f"Process behavior analysis failed: {e}")
            return 0.0
            
    def analyze_file_behavior(self, data: Dict) -> float:
        """Analyze file behavior using ML model."""
        try:
            # Extract features
            features = self._extract_file_features(data)
            
            # Store data for training
            self.file_data.append(features)
            
            # For now, we'll return a placeholder score
            return 0.5
            
        except Exception as e:
            logger.error(f"File behavior analysis failed: {e}")
            return 0.0
            
    def _extract_network_features(self, data: Dict) -> List[float]:
        """Extract network features for ML model."""
        features = []
        
        if self.config["network_features"]["packet_rate"]:
            features.append(data.get("packet_rate", 0))
            
        if self.config["network_features"]["connection_rate"]:
            features.append(data.get("connection_rate", 0))
            
        if self.config["network_features"]["port_scan_rate"]:
            features.append(data.get("port_scan_rate", 0))
            
        if self.config["network_features"]["traffic_volume"]:
            features.append(data.get("traffic_volume", 0))
            
        if self.config["network_features"]["protocol_distribution"]:
            features.extend(data.get("protocol_distribution", [0, 0, 0]))
            
        return features
        
    def _extract_process_features(self, data: Dict) -> List[float]:
        """Extract process features for ML model."""
        features = []
        
        if self.config["process_features"]["cpu_usage"]:
            features.append(data.get("cpu_usage", 0))
            
        if self.config["process_features"]["memory_usage"]:
            features.append(data.get("memory_usage", 0))
            
        if self.config["process_features"]["io_operations"]:
            features.append(data.get("io_operations", 0))
            
        if self.config["process_features"]["network_connections"]:
            features.append(data.get("network_connections", 0))
            
        if self.config["process_features"]["file_access"]:
            features.append(data.get("file_access", 0))
            
        return features
        
    def _extract_file_features(self, data: Dict) -> List[float]:
        """Extract file features for ML model."""
        features = []
        
        if self.config["file_features"]["access_patterns"]:
            features.extend(data.get("access_patterns", [0, 0, 0]))
            
        if self.config["file_features"]["modification_rate"]:
            features.append(data.get("modification_rate", 0))
            
        if self.config["file_features"]["size_changes"]:
            features.append(data.get("size_changes", 0))
            
        if self.config["file_features"]["permission_changes"]:
            features.append(data.get("permission_changes", 0))
            
        return features