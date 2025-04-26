"""
Example script demonstrating basic usage of the Aqua IoT Security Analysis Framework.
"""

import asyncio
from aqua.core import Aqua  # Updated import
from rich.console import Console

console = Console()

async def main():
    """Main function demonstrating framework usage."""
    # Initialize the framework
    framework = Aqua()  # Updated class name
    
    # Example network to scan
    network = "192.168.1.0/24"
    
    console.print("[bold green]Starting IoT Penetration Testing Framework Demo[/bold green]")
    console.print(f"Scanning network: {network}\n")
    
    # Step 1: Discover devices
    console.print("[bold cyan]Step 1: Device Discovery[/bold cyan]")
    devices = await framework.discover_devices(network)
    console.print(f"Discovered {len(devices)} devices\n")
    
    # Step 2: Assess vulnerabilities for each device
    console.print("[bold cyan]Step 2: Vulnerability Assessment[/bold cyan]")
    for device in devices:
        console.print(f"\nAssessing device: {device.ip}")
        vulnerabilities = await framework.assess_device(device)
        console.print(f"Found {len(vulnerabilities)} vulnerabilities")
        
        # Display critical vulnerabilities
        critical_vulns = [v for v in vulnerabilities if v.severity == "critical"]
        if critical_vulns:
            console.print("\n[bold red]Critical Vulnerabilities:[/bold red]")
            for vuln in critical_vulns:
                console.print(f"- {vuln.title}")
    
    # Step 3: Protocol fuzzing
    console.print("\n[bold cyan]Step 3: Protocol Fuzzing[/bold cyan]")
    for device in devices:
        if "mqtt" in [p.value for p in device.protocols]:
            console.print(f"\nFuzzing MQTT on device: {device.ip}")
            results = await framework.fuzz_protocol(device, "mqtt")
            console.print(f"Completed {len(results)} fuzzing attempts")
            
            # Display interesting results
            error_results = [r for r in results if r["status"] == "error"]
            if error_results:
                console.print("\n[bold yellow]Interesting Results:[/bold yellow]")
                for result in error_results[:5]:  # Show first 5 errors
                    console.print(f"- {result['type']}: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    asyncio.run(main())