"""
Vulnerability assessment module for IoT devices.
"""

import asyncio
import aiohttp
import nmap
from loguru import logger
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any

class VulnerabilitySeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class VulnerabilityType(Enum):
    OPEN_PORT = "open_port"
    WEAK_CREDS = "weak_credentials"
    KNOWN_CVE = "known_cve"
    INSECURE_PROTOCOL = "insecure_protocol"
    MISCONFIGURATION = "misconfiguration"

@dataclass
class Vulnerability:
    name: str
    description: str
    severity: VulnerabilitySeverity
    type: VulnerabilityType
    details: Dict[str, Any]

class VulnerabilityAssessor:
    """Class for performing vulnerability assessments on IoT devices."""

    def __init__(self):
        self.nm = nmap.PortScanner()
        self.common_ports = [21, 22, 23, 80, 443, 502, 1883, 5683, 8080, 8883]
        self.common_creds = [
            ("admin", "admin"),
            ("admin", "password"),
            ("root", "root"),
            ("admin", ""),
            ("root", ""),
        ]

    def assess(self, target: str) -> List[Vulnerability]:
        """Perform vulnerability assessment on a target device."""
        vulnerabilities = []
        logger.info(f"Starting vulnerability assessment for {target}")

        # Port scan
        try:
            logger.info("Running port scan...")
            scan_results = self.nm.scan(target, arguments="-sS -sV -T4")
            if target in scan_results["scan"]:
                host_data = scan_results["scan"][target]
                vulnerabilities.extend(self._analyze_ports(host_data))
        except Exception as e:
            logger.error(f"Port scan failed: {e}")

        # Service enumeration
        try:
            logger.info("Checking for common services...")
            vulnerabilities.extend(self._check_services(target))
        except Exception as e:
            logger.error(f"Service check failed: {e}")

        # Default credentials check
        try:
            logger.info("Checking for default credentials...")
            vulnerabilities.extend(self._check_default_creds(target))
        except Exception as e:
            logger.error(f"Credential check failed: {e}")

        logger.info(f"Found {len(vulnerabilities)} potential vulnerabilities")
        return vulnerabilities

    def _analyze_ports(self, host_data: Dict) -> List[Vulnerability]:
        """Analyze open ports and services."""
        vulns = []
        if "tcp" in host_data:
            for port, data in host_data["tcp"].items():
                if data["state"] == "open":
                    # Check for telnet
                    if data.get("name") == "telnet":
                        vulns.append(Vulnerability(
                            name="Telnet Enabled",
                            description="Telnet service is running which transmits data in cleartext",
                            severity=VulnerabilitySeverity.HIGH,
                            type=VulnerabilityType.INSECURE_PROTOCOL,
                            details={"port": port, "service": data}
                        ))
                    # Check for FTP
                    elif data.get("name") == "ftp":
                        vulns.append(Vulnerability(
                            name="FTP Service",
                            description="FTP service detected which may expose sensitive data",
                            severity=VulnerabilitySeverity.MEDIUM,
                            type=VulnerabilityType.INSECURE_PROTOCOL,
                            details={"port": port, "service": data}
                        ))
                    # Check for unencrypted services
                    elif port in [80, 8080]:
                        vulns.append(Vulnerability(
                            name="Unencrypted HTTP",
                            description="HTTP service without TLS encryption",
                            severity=VulnerabilitySeverity.MEDIUM,
                            type=VulnerabilityType.INSECURE_PROTOCOL,
                            details={"port": port, "service": data}
                        ))
        return vulns

    def _check_services(self, target: str) -> List[Vulnerability]:
        """Check for vulnerable services and misconfigurations."""
        vulns = []
        # Check for MQTT
        if self._is_port_open(target, 1883):
            vulns.append(Vulnerability(
                name="Unencrypted MQTT",
                description="MQTT broker without TLS encryption",
                severity=VulnerabilitySeverity.HIGH,
                type=VulnerabilityType.INSECURE_PROTOCOL,
                details={"port": 1883}
            ))
        # Check for CoAP
        if self._is_port_open(target, 5683):
            vulns.append(Vulnerability(
                name="Unencrypted CoAP",
                description="CoAP service without DTLS",
                severity=VulnerabilitySeverity.HIGH,
                type=VulnerabilityType.INSECURE_PROTOCOL,
                details={"port": 5683}
            ))
        return vulns

    def _check_default_creds(self, target: str) -> List[Vulnerability]:
        """Check for default credentials on common services."""
        vulns = []
        # Check web interfaces
        for port in [80, 443, 8080]:
            if self._is_port_open(target, port):
                for username, password in self.common_creds:
                    if self._try_http_auth(target, port, username, password):
                        vulns.append(Vulnerability(
                            name="Default Web Credentials",
                            description=f"Default credentials ({username}:{password}) work on web interface",
                            severity=VulnerabilitySeverity.CRITICAL,
                            type=VulnerabilityType.WEAK_CREDS,
                            details={"port": port, "username": username, "password": password}
                        ))
                        break
        return vulns

    def _is_port_open(self, target: str, port: int) -> bool:
        """Check if a specific port is open."""
        try:
            result = self.nm.scan(target, str(port))
            return (target in result["scan"] and 
                   "tcp" in result["scan"][target] and 
                   port in result["scan"][target]["tcp"] and 
                   result["scan"][target]["tcp"][port]["state"] == "open")
        except:
            return False

    async def _try_http_auth(self, target: str, port: int, username: str, password: str) -> bool:
        """Try HTTP basic auth with given credentials."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"http://{target}:{port}",
                    auth=aiohttp.BasicAuth(username, password),
                    timeout=5,
                    ssl=False
                ) as response:
                    return response.status == 200
        except:
            return False 