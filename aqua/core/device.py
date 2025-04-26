"""
IoT device model and related functionality.
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

class DeviceType(str, Enum):
    """Types of IoT devices."""
    UNKNOWN = "unknown"
    CAMERA = "camera"
    CONTROLLER = "controller"
    SENSOR = "sensor"
    INDUSTRIAL = "industrial"
    SMART_HOME = "smart_home"
    GATEWAY = "gateway"
    BRIDGE = "bridge"
    HUB = "hub"
    LIGHT = "light"
    THERMOSTAT = "thermostat"
    LOCK = "lock"
    SPEAKER = "speaker"
    DISPLAY = "display"
    APPLIANCE = "appliance"
    WEARABLE = "wearable"
    VEHICLE = "vehicle"
    MEDICAL = "medical"
    INFRASTRUCTURE = "infrastructure"

class Protocol(str, Enum):
    """Supported IoT protocols."""
    HTTP = "http"
    HTTPS = "https"
    MQTT = "mqtt"
    MQTTS = "mqtts"
    COAP = "coap"
    COAPS = "coaps"
    UPnP = "upnp"
    MODBUS = "modbus"
    BACNET = "bacnet"
    ZIGBEE = "zigbee"
    ZWAVE = "zwave"
    BLE = "ble"
    KNX = "knx"
    LWM2M = "lwm2m"
    AMQP = "amqp"
    OPCUA = "opcua"
    RTSP = "rtsp"
    ONVIF = "onvif"

class Service(BaseModel):
    """Service running on a device."""
    name: str
    port: int
    protocol: str
    version: Optional[str] = None
    description: Optional[str] = None

class Credential(BaseModel):
    """Device credentials."""
    username: str
    password: str
    type: str  # e.g., "default", "custom", "admin"
    source: str  # e.g., "database", "bruteforce", "discovered"

class Vulnerability(BaseModel):
    """Security vulnerability."""
    name: str
    severity: str  # "critical", "high", "medium", "low"
    description: str
    cve: Optional[str] = None
    cvss: Optional[float] = None
    remediation: Optional[str] = None

class IoTDevice(BaseModel):
    """IoT device model."""
    ip: Optional[str] = None
    mac: Optional[str] = None
    hostname: Optional[str] = None
    device_type: DeviceType = DeviceType.UNKNOWN
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    firmware_version: Optional[str] = None
    protocols: List[Protocol] = []
    open_ports: List[int] = []
    services: Dict[int, str] = {}  # port -> service name
    credentials: List[Credential] = []
    vulnerabilities: List[Vulnerability] = []
    last_seen: Optional[str] = None
    first_seen: Optional[str] = None
    is_online: bool = True
    tags: List[str] = []  # e.g., ["smart_home", "camera", "vulnerable"]
    notes: Optional[str] = None

    def add_vulnerability(self, name: str, severity: str, description: str, 
                         cve: Optional[str] = None, cvss: Optional[float] = None,
                         remediation: Optional[str] = None) -> None:
        """Add a vulnerability to the device."""
        self.vulnerabilities.append(
            Vulnerability(
                name=name,
                severity=severity,
                description=description,
                cve=cve,
                cvss=cvss,
                remediation=remediation
            )
        )

    def add_credential(self, username: str, password: str, 
                      type: str = "default", source: str = "database") -> None:
        """Add credentials to the device."""
        self.credentials.append(
            Credential(
                username=username,
                password=password,
                type=type,
                source=source
            )
        )

    def add_service(self, port: int, name: str, protocol: str,
                   version: Optional[str] = None, description: Optional[str] = None) -> None:
        """Add a service to the device."""
        self.services[port] = name
        # You could also maintain a separate list of Service objects if needed

    def add_tag(self, tag: str) -> None:
        """Add a tag to the device."""
        if tag not in self.tags:
            self.tags.append(tag)

    def update_status(self, is_online: bool) -> None:
        """Update device online status."""
        self.is_online = is_online
        if is_online:
            self.last_seen = datetime.now().isoformat()
        if not self.first_seen:
            self.first_seen = self.last_seen
    
    def to_dict(self) -> Dict:
        """Convert device to dictionary."""
        return self.dict()
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'IoTDevice':
        """Create device from dictionary."""
        return cls(**data) 