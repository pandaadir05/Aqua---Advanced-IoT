"""
Behavioral Analysis and Machine Learning Module for Aqua.
"""

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Optional
import json
from datetime import datetime
from pathlib import Path
import logging
from loguru import logger
from rich.console import Console
from rich.table import Table
import threading
import time
from collections import deque

from aqua.core.alerting import AlertManager, AlertType, AlertSeverity

console = Console()

class BehavioralAnalyzer:
    """Advanced behavioral analysis with machine learning capabilities."""
    
    def __init__(self):
        self.config_path = Path("config/behavioral.json")
        self.config_path.parent.mkdir(exist_ok=True)
        self.load_config()
        
        # Initialize ML models
        self.network_model = IsolationForest(contamination=0.1)
        self.process_model = IsolationForest(contamination=0.1)
        self.file_model = IsolationForest(contamination=0.1)
        
        # Initialize scalers
        self.network_scaler = StandardScaler()
        self.process_scaler = StandardScaler()
        self.file_scaler = StandardScaler()
        
        # Initialize alert manager
        self.alert_manager = AlertManager()
        
        # Data collection
        self.network_data = deque(maxlen=1000)
        self.process_data = deque(maxlen=1000)
        self.file_data = deque(maxlen=1000)
        
        # Start background training
        self.training_thread = threading.Thread(target=self._background_training)
        self.training_thread.daemon = True
        self.training_thread.start()
        
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
                "anomaly_threshold": 0.7,
                "whitelist": {
                    "processes": [],
                    "files": [],
                    "networks": []
                },
                "blacklist": {
                    "processes": [],
                    "files": [],
                    "networks": []
                }
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
            
            # Scale features
            scaled_features = self.network_scaler.transform([features])
            
            # Predict anomaly score
            score = self.network_model.score_samples(scaled_features)[0]
            
            # Store data for training
            self.network_data.append(features)
            
            # Generate alert if anomaly detected
            if score > self.config["anomaly_threshold"]:
                self.alert_manager.create_alert(
                    AlertType.NETWORK,
                    AlertSeverity.HIGH,
                    "Network behavior anomaly detected",
                    {
                        "score": score,
                        "features": features,
                        "data": data
                    }
                )
            
            return score
            
        except Exception as e:
            logger.error(f"Network behavior analysis failed: {e}")
            return 0.0
            
    def analyze_process_behavior(self, data: Dict) -> float:
        """Analyze process behavior using ML model."""
        try:
            # Extract features
            features = self._extract_process_features(data)
            
            # Scale features
            scaled_features = self.process_scaler.transform([features])
            
            # Predict anomaly score
            score = self.process_model.score_samples(scaled_features)[0]
            
            # Store data for training
            self.process_data.append(features)
            
            # Generate alert if anomaly detected
            if score > self.config["anomaly_threshold"]:
                self.alert_manager.create_alert(
                    AlertType.PROCESS,
                    AlertSeverity.HIGH,
                    "Process behavior anomaly detected",
                    {
                        "score": score,
                        "features": features,
                        "data": data
                    }
                )
            
            return score
            
        except Exception as e:
            logger.error(f"Process behavior analysis failed: {e}")
            return 0.0
            
    def analyze_file_behavior(self, data: Dict) -> float:
        """Analyze file behavior using ML model."""
        try:
            # Extract features
            features = self._extract_file_features(data)
            
            # Scale features
            scaled_features = self.file_scaler.transform([features])
            
            # Predict anomaly score
            score = self.file_model.score_samples(scaled_features)[0]
            
            # Store data for training
            self.file_data.append(features)
            
            # Generate alert if anomaly detected
            if score > self.config["anomaly_threshold"]:
                self.alert_manager.create_alert(
                    AlertType.FILE,
                    AlertSeverity.HIGH,
                    "File behavior anomaly detected",
                    {
                        "score": score,
                        "features": features,
                        "data": data
                    }
                )
            
            return score
            
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
        
    def _background_training(self):
        """Background thread for periodic model training."""
        while True:
            try:
                # Train network model
                if len(self.network_data) >= 100:
                    X = np.array(list(self.network_data))
                    self.network_scaler.fit(X)
                    X_scaled = self.network_scaler.transform(X)
                    self.network_model.fit(X_scaled)
                    
                # Train process model
                if len(self.process_data) >= 100:
                    X = np.array(list(self.process_data))
                    self.process_scaler.fit(X)
                    X_scaled = self.process_scaler.transform(X)
                    self.process_model.fit(X_scaled)
                    
                # Train file model
                if len(self.file_data) >= 100:
                    X = np.array(list(self.file_data))
                    self.file_scaler.fit(X)
                    X_scaled = self.file_scaler.transform(X)
                    self.file_model.fit(X_scaled)
                    
            except Exception as e:
                logger.error(f"Background training failed: {e}")
                
            time.sleep(self.config["training_interval"])
            
    def add_to_whitelist(self, item_type: str, item: str):
        """Add item to whitelist."""
        if item_type in self.config["whitelist"]:
            if item not in self.config["whitelist"][item_type]:
                self.config["whitelist"][item_type].append(item)
                self.save_config()
                
    def add_to_blacklist(self, item_type: str, item: str):
        """Add item to blacklist."""
        if item_type in self.config["blacklist"]:
            if item not in self.config["blacklist"][item_type]:
                self.config["blacklist"][item_type].append(item)
                self.save_config()
                
    def remove_from_whitelist(self, item_type: str, item: str):
        """Remove item from whitelist."""
        if item_type in self.config["whitelist"]:
            if item in self.config["whitelist"][item_type]:
                self.config["whitelist"][item_type].remove(item)
                self.save_config()
                
    def remove_from_blacklist(self, item_type: str, item: str):
        """Remove item from blacklist."""
        if item_type in self.config["blacklist"]:
            if item in self.config["blacklist"][item_type]:
                self.config["blacklist"][item_type].remove(item)
                self.save_config()
                
    def is_whitelisted(self, item_type: str, item: str) -> bool:
        """Check if item is whitelisted."""
        return item_type in self.config["whitelist"] and item in self.config["whitelist"][item_type]
        
    def is_blacklisted(self, item_type: str, item: str) -> bool:
        """Check if item is blacklisted."""
        return item_type in self.config["blacklist"] and item in self.config["blacklist"][item_type] 