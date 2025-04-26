"""
Scan profiles for different IoT device types and environments.
"""

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel

class ScanType(str, Enum):
    QUICK = "quick"           # Basic scan with minimal impact
    STANDARD = "standard"     # Standard security scan
    COMPREHENSIVE = "comprehensive"  # In-depth security analysis
    AGGRESSIVE = "aggressive" # Thorough scan with active testing
    CUSTOM = "custom"         # User-defined scan profile

class DeviceCategory(str, Enum):
    CAMERA = "camera"
    ROUTER = "router"
    SMART_HOME = "smart_home"
    INDUSTRIAL = "industrial"
    MEDICAL = "medical"
    GENERIC = "generic"

class ScanProfile(BaseModel):
    """Model for scan profiles."""
    name: str
    description: str
    type: ScanType
    device_category: Optional[DeviceCategory] = DeviceCategory.GENERIC
    ports: List[int] = []
    services: List[str] = []
    checks: List[str] = []
    aggressive: bool = False
    timeout: int = 300  # seconds
    retry_count: int = 2
    custom_parameters: Dict = {}
    
    def to_nmap_args(self) -> str:
        """Convert profile to nmap arguments."""
        args = []
        
        # Timing template based on scan type
        timing_map = {
            ScanType.QUICK: "T3",
            ScanType.STANDARD: "T4", 
            ScanType.COMPREHENSIVE: "T4",
            ScanType.AGGRESSIVE: "T5",
            ScanType.CUSTOM: "T4"  # Default timing for custom
        }
        args.append(f"-{timing_map[self.type]}")
        
        # Version detection
        if self.type in [ScanType.STANDARD, ScanType.COMPREHENSIVE, ScanType.AGGRESSIVE]:
            args.append("-sV")
            
        # OS detection
        if self.type in [ScanType.COMPREHENSIVE, ScanType.AGGRESSIVE]:
            args.append("-O")
            
        # Script scanning
        if self.type == ScanType.COMPREHENSIVE:
            args.append("--script=default,vuln")
        elif self.type == ScanType.AGGRESSIVE:
            args.append("--script=default,vuln,exploit")
            
        # Ports
        if self.ports:
            args.append(f"-p {','.join(map(str, self.ports))}")
            
        # Additional flags for aggressive scans
        if self.aggressive:
            args.append("--max-retries 2")
            args.append("--min-rate 1000")
            
        return " ".join(args)

class ProfileManager:
    """Manager for scan profiles."""
    
    def __init__(self):
        """Initialize with default profiles."""
        self.profiles: Dict[str, ScanProfile] = {}
        self._initialize_default_profiles()
        
    def _initialize_default_profiles(self):
        """Create default scan profiles."""
        # Quick scan profile
        self.profiles["quick"] = ScanProfile(
            name="Quick Scan",
            description="Fast scan with minimal impact",
            type=ScanType.QUICK,
            ports=[21, 22, 23, 80, 443, 1883, 8080, 8883, 5683],
            checks=["open_ports", "default_services"]
        )
        
        # Standard scan profile
        self.profiles["standard"] = ScanProfile(
            name="Standard Scan",
            description="Standard security assessment",
            type=ScanType.STANDARD,
            ports=[21, 22, 23, 25, 53, 80, 443, 445, 1883, 5683, 8080, 8883],
            checks=["open_ports", "default_services", "default_credentials", "known_vulnerabilities"]
        )
        
        # Comprehensive scan profile
        self.profiles["comprehensive"] = ScanProfile(
            name="Comprehensive Scan",
            description="In-depth security analysis",
            type=ScanType.COMPREHENSIVE,
            ports=[1, 21, 22, 23, 25, 53, 80, 110, 139, 143, 443, 445, 465, 502, 1883, 5683, 8080, 8883],
            checks=[
                "open_ports", "default_services", "default_credentials", 
                "known_vulnerabilities", "ssl_tls", "firmware", "brute_force"
            ]
        )
        
        # Aggressive scan profile
        self.profiles["aggressive"] = ScanProfile(
            name="Aggressive Scan",
            description="Thorough scan with active testing",
            type=ScanType.AGGRESSIVE,
            aggressive=True,
            ports=[], # Scan all ports
            checks=[
                "open_ports", "default_services", "default_credentials", 
                "known_vulnerabilities", "ssl_tls", "firmware", "brute_force",
                "fuzzing", "exploitation"
            ]
        )
        
        # Camera profile
        self.profiles["camera"] = ScanProfile(
            name="Camera Scan",
            description="Specialized scan for IP cameras",
            type=ScanType.STANDARD,
            device_category=DeviceCategory.CAMERA,
            ports=[80, 443, 554, 1935, 8000, 8080, 8554, 8800],
            services=["http", "https", "rtsp", "onvif"],
            checks=[
                "open_ports", "default_services", "default_credentials", 
                "known_vulnerabilities", "rtsp_exposure"
            ]
        )
        
        # Router profile
        self.profiles["router"] = ScanProfile(
            name="Router Scan",
            description="Specialized scan for routers and gateways",
            type=ScanType.STANDARD,
            device_category=DeviceCategory.ROUTER,
            ports=[22, 23, 53, 80, 443, 8080, 8443],
            services=["ssh", "telnet", "dns", "http", "https"],
            checks=[
                "open_ports", "default_services", "default_credentials", 
                "known_vulnerabilities", "dns_config", "upnp_exposure"
            ]
        )
        
    def get_profile(self, name: str) -> Optional[ScanProfile]:
        """Get a scan profile by name."""
        return self.profiles.get(name)
        
    def add_profile(self, profile: ScanProfile) -> None:
        """Add or update a scan profile."""
        self.profiles[profile.name.lower()] = profile
        
    def delete_profile(self, name: str) -> bool:
        """Delete a scan profile."""
        if name.lower() in self.profiles:
            del self.profiles[name.lower()]
            return True
        return False
        
    def list_profiles(self) -> List[ScanProfile]:
        """List all available scan profiles."""
        return list(self.profiles.values())
