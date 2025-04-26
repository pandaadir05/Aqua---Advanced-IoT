"""
Core framework class for Aqua - Advanced IoT Security Analysis Framework.
"""

from typing import List, Dict, Optional
from loguru import logger
from pydantic import BaseModel
from ..modules.discovery import DeviceDiscoverer
from ..modules.assessment import VulnerabilityAssessor
from ..modules.fuzzing import ProtocolFuzzer
from ..core.device import IoTDevice
from ..core.vulnerability import Vulnerability

class Aqua:
    """Main framework class for IoT security analysis."""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the Aqua framework.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.discoverer = DeviceDiscoverer()
        self.assessor = VulnerabilityAssessor()
        self.fuzzer = ProtocolFuzzer()
        self._setup_logging()
    
    def _setup_logging(self):
        """Configure logging for the framework."""
        logger.add("aqua.log", rotation="1 day", retention="7 days")
    
    async def discover_devices(self, network: str) -> List[IoTDevice]:
        """
        Discover IoT devices on the network.
        
        Args:
            network: Network range to scan (e.g., "192.168.1.0/24")
            
        Returns:
            List of discovered IoT devices
        """
        logger.info(f"Starting device discovery on network: {network}")
        devices = await self.discoverer.scan(network)
        logger.info(f"Discovered {len(devices)} devices")
        return devices
    
    async def assess_device(self, device: IoTDevice) -> List[Vulnerability]:
        """
        Perform vulnerability assessment on a device.
        
        Args:
            device: IoT device to assess
            
        Returns:
            List of discovered vulnerabilities
        """
        logger.info(f"Starting vulnerability assessment for device: {device.ip}")
        vulnerabilities = await self.assessor.assess(device)
        logger.info(f"Found {len(vulnerabilities)} vulnerabilities")
        return vulnerabilities
    
    async def fuzz_protocol(self, device: IoTDevice, protocol: str) -> List[Dict]:
        """
        Fuzz a specific protocol on a device.
        
        Args:
            device: Target device
            protocol: Protocol to fuzz (e.g., "mqtt", "coap")
            
        Returns:
            List of fuzzing results
        """
        logger.info(f"Starting protocol fuzzing for {protocol} on {device.ip}")
        results = await self.fuzzer.fuzz(device, protocol)
        logger.info(f"Completed fuzzing with {len(results)} findings")
        return results
    
    async def run_full_assessment(self, network: str) -> Dict:
        """
        Run a complete assessment including discovery, vulnerability scanning, and fuzzing.
        
        Args:
            network: Network range to assess
            
        Returns:
            Complete assessment results
        """
        logger.info("Starting full assessment")
        results = {
            "devices": [],
            "vulnerabilities": [],
            "fuzzing_results": []
        }
        
        # Discover devices
        devices = await self.discover_devices(network)
        results["devices"] = devices
        
        # Assess each device
        for device in devices:
            vulns = await self.assess_device(device)
            results["vulnerabilities"].extend(vulns)
            
            # Fuzz common protocols
            for protocol in ["mqtt", "coap", "http"]:
                fuzz_results = await self.fuzz_protocol(device, protocol)
                results["fuzzing_results"].extend(fuzz_results)
        
        logger.info("Completed full assessment")
        return results

# For backward compatibility
IoTPTF = Aqua