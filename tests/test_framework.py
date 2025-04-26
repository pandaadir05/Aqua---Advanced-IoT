"""
Tests for the IoT Penetration Testing Framework.
"""

import pytest
from iotptf.core.framework import IoTPTF
from iotptf.core.device import IoTDevice, DeviceType, Protocol
from iotptf.core.vulnerability import Vulnerability, Severity, VulnerabilityType

@pytest.fixture
def framework():
    """Create a framework instance for testing."""
    return IoTPTF()

@pytest.fixture
def sample_device():
    """Create a sample IoT device for testing."""
    return IoTDevice(
        ip="192.168.1.100",
        mac="00:11:22:33:44:55",
        hostname="test-device",
        device_type=DeviceType.CAMERA,
        manufacturer="Test Corp",
        model="TestCam 1000",
        firmware_version="1.0.0",
        protocols=[Protocol.HTTP, Protocol.MQTT],
        open_ports=[80, 443, 1883],
        services={"http": "nginx", "mqtt": "mosquitto"},
        credentials={"admin": "password"}
    )

@pytest.mark.asyncio
async def test_device_discovery(framework):
    """Test device discovery functionality."""
    # Note: This test requires a test network or mock
    devices = await framework.discover_devices("127.0.0.1/32")
    assert isinstance(devices, list)

@pytest.mark.asyncio
async def test_vulnerability_assessment(framework, sample_device):
    """Test vulnerability assessment functionality."""
    vulnerabilities = await framework.assess_device(sample_device)
    assert isinstance(vulnerabilities, list)
    for vuln in vulnerabilities:
        assert isinstance(vuln, Vulnerability)

@pytest.mark.asyncio
async def test_protocol_fuzzing(framework, sample_device):
    """Test protocol fuzzing functionality."""
    results = await framework.fuzz_protocol(sample_device, "mqtt")
    assert isinstance(results, list)
    for result in results:
        assert isinstance(result, dict)
        assert "type" in result
        assert "status" in result

def test_device_model(sample_device):
    """Test IoT device model functionality."""
    assert sample_device.ip == "192.168.1.100"
    assert sample_device.device_type == DeviceType.CAMERA
    assert Protocol.HTTP in sample_device.protocols
    assert 80 in sample_device.open_ports
    assert "admin" in sample_device.credentials

def test_vulnerability_model():
    """Test vulnerability model functionality."""
    vuln = Vulnerability(
        id="test-vuln-001",
        title="Test Vulnerability",
        description="This is a test vulnerability",
        severity=Severity.HIGH,
        type=VulnerabilityType.AUTHENTICATION,
        remediation="Fix the vulnerability",
        affected_components=["web interface"]
    )
    
    assert vuln.id == "test-vuln-001"
    assert vuln.severity == Severity.HIGH
    assert vuln.type == VulnerabilityType.AUTHENTICATION
    assert "web interface" in vuln.affected_components

@pytest.mark.asyncio
async def test_full_assessment(framework):
    """Test full assessment functionality."""
    # Note: This test requires a test network or mock
    results = await framework.run_full_assessment("127.0.0.1/32")
    assert isinstance(results, dict)
    assert "devices" in results
    assert "vulnerabilities" in results
    assert "fuzzing_results" in results 