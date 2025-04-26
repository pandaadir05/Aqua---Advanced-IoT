"""
Aqua API Client - Simple API integration client for Aqua IoT Security Platform.
"""

import requests
import json
from typing import Dict, List, Optional, Union, Any

class AquaApiClient:
    """API Client for Aqua IoT Security Platform."""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL of the Aqua API server
            api_key: API key for authentication (if required)
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({"X-API-Key": api_key})
    
    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, 
                     data: Optional[Dict] = None, json_data: Optional[Dict] = None) -> Dict:
        """
        Make a request to the API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            params: URL parameters
            data: Form data
            json_data: JSON data
            
        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json_data
            )
            response.raise_for_status()
            
            if response.content:
                return response.json()
            return {}
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
    
    # Device methods
    def get_devices(self) -> List[Dict]:
        """Get all devices."""
        return self._make_request("GET", "/api/devices")
    
    def get_device(self, device_id: str) -> Dict:
        """Get a specific device by ID."""
        return self._make_request("GET", f"/api/devices/{device_id}")
    
    def add_device(self, device_data: Dict) -> Dict:
        """Add a new device."""
        return self._make_request("POST", "/api/devices", json_data=device_data)
    
    def update_device(self, device_id: str, device_data: Dict) -> Dict:
        """Update a device."""
        return self._make_request("PUT", f"/api/devices/{device_id}", json_data=device_data)
    
    def delete_device(self, device_id: str) -> Dict:
        """Delete a device."""
        return self._make_request("DELETE", f"/api/devices/{device_id}")
    
    # Vulnerability methods
    def get_vulnerabilities(self, device_id: Optional[str] = None) -> List[Dict]:
        """Get all vulnerabilities, optionally filtered by device."""
        params = {}
        if device_id:
            params["device_id"] = device_id
        return self._make_request("GET", "/api/vulnerabilities", params=params)
    
    # Scan methods
    def start_scan(self, target: str, scan_type: str = "full", options: Optional[Dict] = None) -> Dict:
        """Start a new scan."""
        data = {
            "target": target,
            "scan_type": scan_type
        }
        if options:
            data.update(options)
        return self._make_request("POST", "/api/scans", json_data=data)
    
    def get_scan_status(self, scan_id: str) -> Dict:
        """Get the status of a scan."""
        return self._make_request("GET", f"/api/scans/{scan_id}")
    
    def get_scan_results(self, scan_id: str) -> Dict:
        """Get the results of a scan."""
        return self._make_request("GET", f"/api/scans/{scan_id}/results")
    
    def stop_scan(self, scan_id: str) -> Dict:
        """Stop a running scan."""
        return self._make_request("POST", f"/api/scans/{scan_id}/stop")
