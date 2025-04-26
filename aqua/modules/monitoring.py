"""
Real-time IoT device monitoring module.
"""

import asyncio
import time
import json
import socket
import struct
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple, Any
import ipaddress
from scapy.all import ARP, Ether, srp
from loguru import logger
import websockets
from ..core.device import IoTDevice, Protocol

class DeviceMonitor:
    """Real-time IoT device monitoring system."""
    
    def __init__(self):
        """Initialize the device monitor."""
        self.devices: Dict[str, IoTDevice] = {}  # IP -> Device
        self.device_history: Dict[str, List[Dict]] = {}  # IP -> History
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.running = False
        self.monitoring_task = None
        self.ws_server = None
        
    async def start_monitoring(self, network: str, interval: int = 60):
        """
        Start monitoring devices on the network.
        
        Args:
            network: Network CIDR (e.g. "192.168.1.0/24")
            interval: Polling interval in seconds
        """
        if self.running:
            logger.warning("Monitoring is already running")
            return
            
        self.running = True
        logger.info(f"Starting device monitoring on network {network} with {interval}s interval")
        
        # Start websocket server
        self.ws_server = await websockets.serve(self._ws_handler, "0.0.0.0", 8001)
        
        # Start monitoring loop
        self.monitoring_task = asyncio.create_task(self._monitoring_loop(network, interval))
        
    async def stop_monitoring(self):
        """Stop the monitoring process."""
        if not self.running:
            logger.warning("Monitoring is not running")
            return
            
        self.running = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            
        if self.ws_server:
            self.ws_server.close()
            await self.ws_server.wait_closed()
            
        logger.info("Device monitoring stopped")
        
    async def _monitoring_loop(self, network: str, interval: int):
        """
        Main monitoring loop.
        
        Args:
            network: Network CIDR
            interval: Polling interval in seconds
        """
        try:
            while self.running:
                start_time = time.time()
                
                # Discover active devices
                devices = await self._scan_network(network)
                
                # Update device status
                updates = []
                for ip, device in devices.items():
                    if ip in self.devices:
                        # Existing device, check for changes
                        old_device = self.devices[ip]
                        changes = self._detect_changes(old_device, device)
                        if changes:
                            updates.append({
                                "type": "device_changed",
                                "device": device.dict(),
                                "changes": changes
                            })
                            
                            # Record history
                            self._record_history(ip, "changed", changes)
                    else:
                        # New device
                        updates.append({
                            "type": "device_new",
                            "device": device.dict()
                        })
                        
                        # Record history
                        self._record_history(ip, "new")
                
                # Check for devices that went offline
                for ip in list(self.devices.keys()):
                    if ip not in devices:
                        updates.append({
                            "type": "device_offline",
                            "device": self.devices[ip].dict()
                        })
                        
                        # Record history
                        self._record_history(ip, "offline")
                
                # Update device cache
                self.devices = devices
                
                # Send updates to all connected websocket clients
                if updates:
                    await self._broadcast_updates(updates)
                
                # Sleep until next interval
                elapsed = time.time() - start_time
                sleep_time = max(0, interval - elapsed)
                await asyncio.sleep(sleep_time)
                
        except asyncio.CancelledError:
            logger.info("Monitoring task cancelled")
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
            
    async def _scan_network(self, network: str) -> Dict[str, IoTDevice]:
        """
        Scan network for active devices.
        
        Args:
            network: Network CIDR
            
        Returns:
            Dictionary of IP to IoTDevice
        """
        devices = {}
        try:
            # Use ARP to quickly discover devices
            ip_network = ipaddress.IPv4Network(network)
            arp_request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=network)
            result = srp(arp_request, timeout=3, verbose=0)[0]
            
            for sent, received in result:
                ip = received.psrc
                mac = received.hwsrc
                
                # Basic device info
                device = IoTDevice(
                    ip=ip,
                    mac=mac,
                    hostname=self._get_hostname(ip),
                    last_seen=datetime.now().isoformat(),
                    first_seen=datetime.now().isoformat() if ip not in self.devices else self.devices[ip].first_seen,
                    is_online=True
                )
                
                # Additional checks could be done here
                open_ports = self._quick_port_scan(ip)
                if open_ports:
                    device.open_ports = open_ports
                    
                devices[ip] = device
                
        except Exception as e:
            logger.error(f"Error scanning network: {e}")
            
        return devices
        
    def _get_hostname(self, ip: str) -> Optional[str]:
        """Get hostname for an IP address."""
        try:
            return socket.gethostbyaddr(ip)[0]
        except:
            return None
            
    def _quick_port_scan(self, ip: str) -> List[int]:
        """Perform a quick port scan on common ports."""
        common_ports = [22, 23, 80, 443, 1883, 8080, 8883, 5683]
        open_ports = []
        
        for port in common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                result = sock.connect_ex((ip, port))
                if result == 0:
                    open_ports.append(port)
                sock.close()
            except:
                pass
                
        return open_ports
        
    def _detect_changes(self, old_device: IoTDevice, new_device: IoTDevice) -> Dict[str, Any]:
        """
        Detect changes between device states.
        
        Args:
            old_device: Previous device state
            new_device: Current device state
            
        Returns:
            Dictionary of changes
        """
        changes = {}
        
        if old_device.hostname != new_device.hostname:
            changes["hostname"] = {"old": old_device.hostname, "new": new_device.hostname}
            
        if set(old_device.open_ports) != set(new_device.open_ports):
            added = set(new_device.open_ports) - set(old_device.open_ports)
            removed = set(old_device.open_ports) - set(new_device.open_ports)
            changes["ports"] = {"added": list(added), "removed": list(removed)}
            
        if old_device.is_online != new_device.is_online:
            changes["online_status"] = {"old": old_device.is_online, "new": new_device.is_online}
            
        return changes
        
    def _record_history(self, ip: str, event_type: str, details: Optional[Dict] = None) -> None:
        """
        Record an event in device history.
        
        Args:
            ip: Device IP
            event_type: Event type (new, changed, offline)
            details: Optional event details
        """
        if ip not in self.device_history:
            self.device_history[ip] = []
            
        self.device_history[ip].append({
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": details
        })
        
        # Limit history size
        if len(self.device_history[ip]) > 100:
            self.device_history[ip] = self.device_history[ip][-100:]
            
    async def _broadcast_updates(self, updates: List[Dict]) -> None:
        """
        Broadcast updates to all connected websocket clients.
        
        Args:
            updates: List of update events
        """
        if not self.clients:
            return
            
        # Prepare message
        message = json.dumps({
            "timestamp": datetime.now().isoformat(),
            "updates": updates
        })
        
        # Send to all clients
        closed_clients = set()
        for client in self.clients:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                closed_clients.add(client)
                
        # Remove closed connections
        self.clients -= closed_clients
        
    async def _ws_handler(self, websocket, path):
        """
        Handle websocket connections.
        
        Args:
            websocket: WebSocket connection
            path: Connection path
        """
        # Register client
        self.clients.add(websocket)
        
        # Send current device list
        if self.devices:
            try:
                await websocket.send(json.dumps({
                    "timestamp": datetime.now().isoformat(),
                    "type": "device_list",
                    "devices": [d.dict() for d in self.devices.values()]
                }))
            except:
                pass
        
        # Keep connection open until closed
        try:
            async for message in websocket:
                # Process any client commands here
                pass
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.remove(websocket)
