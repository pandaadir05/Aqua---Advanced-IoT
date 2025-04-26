"""
Advanced IoT device discovery and analysis module.
"""

import asyncio
import os
import sys
import platform
from typing import List, Dict, Set
import nmap
import socket
import requests
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from zeroconf import ServiceBrowser, Zeroconf
from loguru import logger
from bleak import BleakScanner
from datetime import datetime
from ..core.device import IoTDevice, DeviceType, Protocol, Vulnerability

# Common IoT ports and services
IOT_PORTS = {
    # MQTT
    1883: "MQTT",
    8883: "MQTT-SSL",
    # HTTP/HTTPS
    80: "HTTP",
    443: "HTTPS",
    8080: "HTTP-ALT",
    # CoAP
    5683: "CoAP",
    5684: "CoAP-DTLS",
    # UPnP
    1900: "UPnP",
    # Modbus
    502: "Modbus",
    # BACnet
    47808: "BACnet",
    # Zigbee
    17754: "Zigbee",
    # Z-Wave
    4123: "Z-Wave",
    # KNX
    3671: "KNX",
    # LWM2M
    5685: "LWM2M",
    # AMQP
    5672: "AMQP",
    5671: "AMQP-SSL",
    # OPC UA
    4840: "OPC UA",
    # RTSP
    554: "RTSP",
    # ONVIF
    3702: "ONVIF",
    # WeMo
    49152: "WeMo",
    # Philips Hue
    80: "Philips Hue",
    443: "Philips Hue SSL",
    # Nest
    9553: "Nest",
    # Samsung SmartThings
    39500: "SmartThings",
    # Apple HomeKit
    5353: "HomeKit",
    # Google Home
    8008: "Google Home",
    8009: "Google Home SSL",
    # Amazon Echo
    4070: "Amazon Echo",
    # Sonos
    1400: "Sonos",
    # IFTTT
    8080: "IFTTT",
    # Home Assistant
    8123: "Home Assistant",
}

# Common IoT device fingerprints
DEVICE_FINGERPRINTS = {
    "philips_hue": {
        "ports": [80, 443],
        "services": ["Philips Hue"],
        "manufacturer": "Philips",
        "model": "Hue Bridge"
    },
    "nest": {
        "ports": [9553],
        "services": ["Nest"],
        "manufacturer": "Google",
        "model": "Nest"
    },
    "amazon_echo": {
        "ports": [4070],
        "services": ["Amazon Echo"],
        "manufacturer": "Amazon",
        "model": "Echo"
    },
    "google_home": {
        "ports": [8008, 8009],
        "services": ["Google Home"],
        "manufacturer": "Google",
        "model": "Home"
    },
    "sonos": {
        "ports": [1400],
        "services": ["Sonos"],
        "manufacturer": "Sonos",
        "model": "Speaker"
    },
    "smartthings": {
        "ports": [39500],
        "services": ["SmartThings"],
        "manufacturer": "Samsung",
        "model": "SmartThings Hub"
    },
    "homekit": {
        "ports": [5353],
        "services": ["HomeKit"],
        "manufacturer": "Apple",
        "model": "HomeKit"
    }
}

class DeviceDiscoverer:
    """Advanced IoT device discovery and analysis class."""
    
    def __init__(self):
        """Initialize the device discoverer."""
        try:
            if platform.system() == 'Windows':
                nmap_paths = [
                    r'C:\Program Files (x86)\Nmap\nmap.exe',
                    r'C:\Program Files\Nmap\nmap.exe'
                ]
                if not any(os.path.exists(path) for path in nmap_paths):
                    raise RuntimeError(
                        "Nmap is not installed. Please install Nmap from https://nmap.org/download.html "
                        "and make sure it's added to your system PATH during installation."
                    )
            
            self.nm = nmap.PortScanner()
            self.zeroconf = Zeroconf()
            self.discovered_devices: Dict[str, IoTDevice] = {}
            self.executor = ThreadPoolExecutor(max_workers=4)
        except Exception as e:
            logger.error(f"Failed to initialize device discoverer: {e}")
            raise

    async def scan(self, network: str) -> List[IoTDevice]:
        """
        Perform comprehensive IoT device discovery and analysis.
        """
        logger.info(f"Starting comprehensive IoT device scan on {network}")
        devices = []
        
        try:
            # Run initial host discovery
            hosts = await self._discover_hosts(network)
            if not hosts:
                logger.warning("No hosts found in the specified network range")
                return []
            
            logger.info(f"Found {len(hosts)} active hosts")
            
            # Process each host with multiple scanning techniques
            for host in hosts:
                device = await self._scan_host(host)
                if device:
                    devices.append(device)
            
            # Run additional discovery methods
            try:
                ble_devices = await self._ble_scan()
                devices.extend(ble_devices)
            except Exception as e:
                logger.warning(f"BLE scan skipped: {e}")
            
            try:
                zeroconf_devices = await self._zeroconf_scan()
                devices.extend(zeroconf_devices)
            except Exception as e:
                logger.warning(f"Zeroconf scan skipped: {e}")
            
            # Perform vulnerability assessment
            for device in devices:
                await self._assess_vulnerabilities(device)
            
            logger.info(f"Scan completed. Found {len(devices)} IoT devices")
            return devices
            
        except Exception as e:
            logger.error(f"Scan failed: {e}")
            raise

    async def _scan_host(self, host: str) -> IoTDevice:
        """Perform comprehensive scanning of a single host."""
        try:
            logger.info(f"Scanning host {host}")
            
            # Try to get hostname
            try:
                hostname = socket.gethostbyaddr(host)[0]
            except:
                hostname = ""
            
            # Try to get MAC address
            mac = self._get_mac_address(host)
            
            # Try different scanning techniques
            open_ports = set()
            
            # 1. Quick scan of common IoT ports
            try:
                result = await asyncio.wait_for(
                    asyncio.get_running_loop().run_in_executor(
                        self.executor,
                        lambda: self.nm.scan(
                            hosts=host,
                            arguments=f'-p {",".join(map(str, IOT_PORTS.keys()))} -T4 --max-rtt-timeout 1000ms'
                        )
                    ),
                    timeout=10.0
                )
                if host in self.nm.all_hosts():
                    open_ports.update({
                        port for port in IOT_PORTS.keys()
                        if port in self.nm[host].get('tcp', {}) and self.nm[host]['tcp'][port]['state'] == 'open'
                    })
            except Exception as e:
                logger.debug(f"Quick scan failed for {host}: {e}")
            
            # 2. If no ports found, try a more aggressive scan
            if not open_ports:
                try:
                    logger.info(f"No ports found in quick scan for {host}, trying aggressive scan")
                    result = await asyncio.wait_for(
                        asyncio.get_running_loop().run_in_executor(
                            self.executor,
                            lambda: self.nm.scan(
                                hosts=host,
                                arguments='-p- -T4 --max-rtt-timeout 1000ms'
                            )
                        ),
                        timeout=30.0
                    )
                    if host in self.nm.all_hosts():
                        open_ports.update({
                            port for port in self.nm[host].get('tcp', {})
                            if self.nm[host]['tcp'][port]['state'] == 'open'
                        })
                except Exception as e:
                    logger.debug(f"Aggressive scan failed for {host}: {e}")
            
            # 3. Try service detection
            if open_ports:
                try:
                    result = await asyncio.wait_for(
                        asyncio.get_running_loop().run_in_executor(
                            self.executor,
                            lambda: self.nm.scan(
                                hosts=host,
                                arguments=f'-p {",".join(map(str, open_ports))} -sV -T4'
                            )
                        ),
                        timeout=20.0
                    )
                except Exception as e:
                    logger.debug(f"Service detection failed for {host}: {e}")
            
            # Create device object
            device = IoTDevice(
                ip=host,
                mac=mac,
                hostname=hostname,
                device_type=self._identify_device_type(open_ports),
                open_ports=list(open_ports),
                services=self._get_services(host, open_ports),
                protocols=self._detect_protocols(open_ports),
                last_seen=datetime.now().isoformat(),
                first_seen=datetime.now().isoformat(),
                is_online=True
            )
            
            # Try to identify manufacturer and model
            manufacturer, model = self._identify_device_model(open_ports, device.services)
            if manufacturer:
                device.manufacturer = manufacturer
            if model:
                device.model = model
            
            return device
            
        except Exception as e:
            logger.error(f"Host scan failed for {host}: {e}")
            return None

    def _get_services(self, host: str, open_ports: Set[int]) -> Dict[int, str]:
        """Get services running on open ports."""
        services = {}
        try:
            if host in self.nm.all_hosts():
                for port in open_ports:
                    if port in self.nm[host].get('tcp', {}):
                        service = self.nm[host]['tcp'][port].get('name', 'unknown')
                        services[port] = service
        except:
            pass
        return services

    def _identify_device_type(self, open_ports: Set[int]) -> DeviceType:
        """Identify device type based on open ports."""
        if any(port in [80, 443, 8080] for port in open_ports):
            return DeviceType.CAMERA
        elif any(port in [1883, 8883] for port in open_ports):
            return DeviceType.CONTROLLER
        elif any(port in [5683, 5684] for port in open_ports):
            return DeviceType.SENSOR
        elif any(port in [502] for port in open_ports):
            return DeviceType.INDUSTRIAL
        elif any(port in [1900] for port in open_ports):
            return DeviceType.SMART_HOME
        return DeviceType.UNKNOWN

    def _identify_device_model(self, open_ports: Set[int], services: Dict[int, str]) -> tuple:
        """Identify device manufacturer and model based on ports and services."""
        for fingerprint_name, fingerprint in DEVICE_FINGERPRINTS.items():
            if all(port in open_ports for port in fingerprint['ports']):
                return fingerprint['manufacturer'], fingerprint['model']
        return None, None

    def _detect_protocols(self, open_ports: Set[int]) -> List[Protocol]:
        """Detect supported protocols based on open ports."""
        protocols = []
        
        if any(port in [1883, 8883] for port in open_ports):
            protocols.append(Protocol.MQTT)
        if any(port in [5683, 5684] for port in open_ports):
            protocols.append(Protocol.COAP)
        if any(port in [80, 443, 8080] for port in open_ports):
            protocols.append(Protocol.HTTP)
            if 443 in open_ports:
                protocols.append(Protocol.HTTPS)
        if any(port in [502] for port in open_ports):
            protocols.append(Protocol.MODBUS)
        if any(port in [1900] for port in open_ports):
            protocols.append(Protocol.UPnP)
        
        return protocols

    def _get_mac_address(self, host: str) -> str:
        """Get MAC address of a host."""
        try:
            return self.nm[host].get('mac', {}).get('address')
        except:
            return None

    async def _discover_hosts(self, network: str) -> List[str]:
        """Discover active hosts in the network range."""
        try:
            logger.info(f"Discovering hosts in network range: {network}")
            result = await asyncio.wait_for(
                asyncio.get_running_loop().run_in_executor(
                    self.executor,
                    lambda: self.nm.scan(
                        hosts=network,
                        arguments='-sn -T4 --max-rtt-timeout 1000ms'
                    )
                ),
                timeout=30.0
            )
            return list(result['scan'].keys())
        except Exception as e:
            logger.error(f"Host discovery failed: {e}")
            return []

    async def _assess_vulnerabilities(self, device: IoTDevice) -> None:
        """Assess common IoT vulnerabilities."""
        # Check for default credentials
        if device.manufacturer and device.model:
            for creds in self._check_default_credentials(device):
                device.add_vulnerability(
                    name="Default Credentials",
                    severity="high",
                    description=f"Device uses default credentials: {creds}",
                    remediation="Change default credentials immediately"
                )
        
        # Check for unencrypted protocols
        if Protocol.HTTP in device.protocols and Protocol.HTTPS not in device.protocols:
            device.add_vulnerability(
                name="Unencrypted Communication",
                severity="medium",
                description="Device uses unencrypted HTTP instead of HTTPS",
                remediation="Enable HTTPS or use a secure protocol"
            )
        
        # Check for open administrative interfaces
        if 80 in device.open_ports or 443 in device.open_ports:
            device.add_vulnerability(
                name="Open Administrative Interface",
                severity="medium",
                description="Device has an open web interface",
                remediation="Restrict access to administrative interfaces"
            )
        
        # Check for UPnP enabled
        if 1900 in device.open_ports:
            device.add_vulnerability(
                name="UPnP Enabled",
                severity="medium",
                description="UPnP is enabled, which can be a security risk",
                remediation="Disable UPnP if not required"
            )

    def _check_default_credentials(self, device: IoTDevice) -> List[str]:
        """Check for default credentials based on manufacturer and model."""
        default_creds = {
            "Philips": {
                "Hue Bridge": ["admin:admin", "root:root"]
            },
            "Google": {
                "Nest": ["admin:admin"]
            },
            "Amazon": {
                "Echo": ["admin:admin"]
            }
        }
        
        if device.manufacturer in default_creds and device.model in default_creds[device.manufacturer]:
            return default_creds[device.manufacturer][device.model]
        return []

    async def _ble_scan(self) -> List[IoTDevice]:
        """Perform Bluetooth LE scan for IoT devices."""
        try:
            logger.info("Starting BLE scan")
            devices = []
            scanner = BleakScanner()
            
            ble_devices = await scanner.discover(timeout=10.0)
            
            for device in ble_devices:
                iot_device = IoTDevice(
                    ip=None,
                    mac=device.address,
                    hostname=device.name or f"BLE-{device.address}",
                    device_type=DeviceType.UNKNOWN,
                    protocols=[Protocol.BLE]
                )
                devices.append(iot_device)
            
            return devices
        except Exception as e:
            logger.error(f"BLE scan failed: {e}")
            return []

    async def _zeroconf_scan(self) -> List[IoTDevice]:
        """Perform Zeroconf/mDNS scan for IoT devices."""
        try:
            logger.info("Starting Zeroconf scan")
            # Implementation for Zeroconf scanning
            # This is a placeholder - actual implementation would use ServiceBrowser
            return []
        except Exception as e:
            logger.error(f"Zeroconf scan failed: {e}")
            return [] 