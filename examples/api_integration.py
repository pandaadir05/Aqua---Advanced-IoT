"""
Example script demonstrating API integration with the Aqua IoT Security Platform.
"""

import asyncio
import json
from aqua.api import AquaApiClient

def print_section(title):
    """Print a section header."""
    print(f"\n{'=' * 50}")
    print(f"  {title}")
    print(f"{'=' * 50}\n")

def main():
    """Demonstrate API client usage."""
    # Create API client
    client = AquaApiClient(base_url="http://localhost:8000")
    
    # Get devices
    print_section("Getting all devices")
    try:
        devices = client.get_devices()
        print(f"Found {len(devices)} devices:")
        for device in devices:
            print(f"- {device.get('ip')} ({device.get('device_type', 'unknown')})")
    except Exception as e:
        print(f"Error getting devices: {e}")
    
    # Start a scan
    print_section("Starting a scan")
    try:
        scan = client.start_scan(target="192.168.1.0/24", scan_type="quick")
        print(f"Started scan with ID: {scan.get('scan_id')}")
        
        # Wait for scan to complete
        print("Waiting for scan to complete...")
        scan_id = scan.get('scan_id')
        while True:
            status = client.get_scan_status(scan_id)
            if status.get('status') != 'running':
                break
            print(f"Scan progress: {status.get('progress', 0)}%")
            asyncio.sleep(1)
        
        # Get scan results
        results = client.get_scan_results(scan_id)
        print(f"\nScan completed with status: {status.get('status')}")
        print(f"Discovered {len(results.get('devices', []))} devices")
        print(f"Found {len(results.get('vulnerabilities', []))} vulnerabilities")
        
        # Print detailed results
        for vuln in results.get('vulnerabilities', []):
            print(f"- [{vuln.get('severity', 'unknown')}] {vuln.get('name')}: {vuln.get('description')}")
            
    except Exception as e:
        print(f"Error during scanning: {e}")
    
    # Add a device manually
    print_section("Adding a device manually")
    try:
        new_device = {
            "ip": "192.168.1.200",
            "hostname": "smart-thermostat",
            "device_type": "thermostat",
            "manufacturer": "SmartHome",
            "model": "TH-2000"
        }
        
        result = client.add_device(new_device)
        print(f"Device added with ID: {result.get('id')}")
    except Exception as e:
        print(f"Error adding device: {e}")

if __name__ == "__main__":
    main()
