import nmap
import socket
import requests
import ssl
import json
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import paramiko
import concurrent.futures
import re
import os
from pathlib import Path

@dataclass
class Service:
    port: int
    name: str
    version: Optional[str] = None
    banner: Optional[str] = None
    protocol: str = "tcp"

@dataclass
class Vulnerability:
    cve_id: str
    severity: str
    description: str
    affected_service: str
    remediation: str
    cvss_score: float

@dataclass
class Device:
    ip: str
    hostname: Optional[str] = None
    mac_address: Optional[str] = None
    manufacturer: Optional[str] = None
    services: List[Service] = None
    vulnerabilities: List[Vulnerability] = None
    last_seen: datetime = None
    is_online: bool = True

class IoTPTFScanner:
    def __init__(self):
        self.nm = nmap.PortScanner()
        self.vulnerability_db = self._load_vulnerability_db()
        
    def _load_vulnerability_db(self) -> Dict:
        db_path = Path(__file__).parent / "data" / "vulnerabilities.json"
        if db_path.exists():
            with open(db_path) as f:
                return json.load(f)
        return {}
    
    def scan_target(self, target: str, ports: str = "1-1000") -> Device:
        """Perform a comprehensive scan of the target."""
        device = Device(ip=target)
        
        # Basic port scan
        self.nm.scan(target, ports, arguments='-sV -sC -O --version-intensity 5')
        
        if target in self.nm.all_hosts():
            host = self.nm[target]
            
            # Get hostname
            try:
                device.hostname = socket.gethostbyaddr(target)[0]
            except:
                pass
                
            # Get MAC address and manufacturer
            if 'mac' in host['addresses']:
                device.mac_address = host['addresses']['mac']
                device.manufacturer = self._get_manufacturer(device.mac_address)
            
            # Scan services
            device.services = []
            for proto in host.all_protocols():
                ports = host[proto].keys()
                for port in ports:
                    service = host[proto][port]
                    device.services.append(Service(
                        port=port,
                        name=service['name'],
                        version=service.get('version', ''),
                        banner=service.get('product', ''),
                        protocol=proto
                    ))
            
            # Detect vulnerabilities
            device.vulnerabilities = self._detect_vulnerabilities(device)
            device.last_seen = datetime.now()
            
        return device
    
    def _get_manufacturer(self, mac: str) -> Optional[str]:
        """Get manufacturer from MAC address."""
        # This is a simplified version. In a real implementation, you'd use a MAC vendor database
        return "Unknown Manufacturer"
    
    def _detect_vulnerabilities(self, device: Device) -> List[Vulnerability]:
        """Detect vulnerabilities based on services and versions."""
        vulnerabilities = []
        
        for service in device.services:
            # Check for common vulnerabilities
            if service.name == "http" or service.name == "https":
                vulns = self._check_web_vulnerabilities(device.ip, service)
                vulnerabilities.extend(vulns)
            
            if service.name == "ssh":
                vulns = self._check_ssh_vulnerabilities(device.ip, service)
                vulnerabilities.extend(vulns)
            
            # Add more service-specific checks here
            
        return vulnerabilities
    
    def _check_web_vulnerabilities(self, ip: str, service: Service) -> List[Vulnerability]:
        """Check for web-related vulnerabilities."""
        vulns = []
        try:
            # Check SSL/TLS configuration
            if service.name == "https":
                context = ssl.create_default_context()
                with socket.create_connection((ip, service.port)) as sock:
                    with context.wrap_socket(sock, server_hostname=ip) as ssock:
                        cert = ssock.getpeercert()
                        if not cert:
                            vulns.append(Vulnerability(
                                cve_id="CVE-2023-XXXX",
                                severity="High",
                                description="Invalid SSL certificate",
                                affected_service=f"HTTPS ({service.port})",
                                remediation="Install valid SSL certificate",
                                cvss_score=7.5
                            ))
            
            # Check for common web vulnerabilities
            url = f"http{'s' if service.name == 'https' else ''}://{ip}:{service.port}"
            response = requests.get(url, timeout=5)
            
            # Check for outdated server software
            server_header = response.headers.get('Server', '')
            if "Apache" in server_header and "2.4" not in server_header:
                vulns.append(Vulnerability(
                    cve_id="CVE-2023-XXXX",
                    severity="Medium",
                    description="Outdated Apache version",
                    affected_service=f"HTTP ({service.port})",
                    remediation="Update Apache to latest version",
                    cvss_score=6.5
                ))
            
        except Exception as e:
            pass
            
        return vulns
    
    def _check_ssh_vulnerabilities(self, ip: str, service: Service) -> List[Vulnerability]:
        """Check for SSH-related vulnerabilities."""
        vulns = []
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(ip, port=service.port, timeout=5)
            
            # Check SSH version
            transport = client.get_transport()
            if transport:
                remote_version = transport.remote_version
                if "OpenSSH" in remote_version and "7.9" not in remote_version:
                    vulns.append(Vulnerability(
                        cve_id="CVE-2023-XXXX",
                        severity="High",
                        description="Outdated OpenSSH version",
                        affected_service=f"SSH ({service.port})",
                        remediation="Update OpenSSH to latest version",
                        cvss_score=8.0
                    ))
            
            client.close()
        except Exception as e:
            pass
            
        return vulns
    
    def scan_network(self, network: str) -> List[Device]:
        """Scan an entire network."""
        devices = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_ip = {
                executor.submit(self.scan_target, f"{network}.{i}"): f"{network}.{i}"
                for i in range(1, 255)
            }
            
            for future in concurrent.futures.as_completed(future_to_ip):
                ip = future_to_ip[future]
                try:
                    device = future.result()
                    if device.services:  # Only add devices with open services
                        devices.append(device)
                except Exception as e:
                    pass
                    
        return devices 