"""
Command-line interface for IoT Penetration Testing Framework.
"""

import sys
import asyncio
import click
from loguru import logger
from ..modules.discovery import DeviceDiscoverer
from ..modules.assessment import VulnerabilityAssessor
from ..modules.fuzzing import ProtocolFuzzer, FuzzingProtocol

def main():
    """Main entry point for the IoT Penetration Testing Framework CLI."""
    cli()

@click.group()
def cli():
    """IoT Penetration Testing Framework CLI."""
    pass

@cli.command()
@click.argument('network')
def discover(network):
    """Discover IoT devices on the network."""
    try:
        discoverer = DeviceDiscoverer()
        
        async def run_discovery():
            devices = await discoverer.scan(network)
            for device in devices:
                click.echo(f"Found device: {device}")
            return devices
            
        if sys.platform == 'win32':
            # Windows requires a different event loop policy
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            
        asyncio.run(run_discovery())
        
    except Exception as e:
        logger.error(f"Discovery failed: {e}")
        sys.exit(1)

@cli.command()
@click.argument('target')
def assess(target):
    """Assess vulnerabilities of an IoT device."""
    try:
        assessor = VulnerabilityAssessor()
        vulnerabilities = assessor.assess(target)
        for vuln in vulnerabilities:
            click.echo(f"Found vulnerability: {vuln}")
    except Exception as e:
        logger.error(f"Assessment failed: {e}")
        sys.exit(1)

@cli.command()
@click.argument('target')
@click.option('--port', type=int, default=80, help='Target port')
@click.option('--protocol', type=click.Choice([p.value for p in FuzzingProtocol]), default='http', help='Protocol to fuzz')
def fuzz(target, port, protocol):
    """Fuzz an IoT device protocol."""
    try:
        fuzzer = ProtocolFuzzer()
        protocol_enum = FuzzingProtocol(protocol)
        
        async def run_fuzzing():
            results = await fuzzer.fuzz(target, port, protocol_enum)
            for result in results:
                click.echo(f"Fuzzing result: {result}")
            return results
            
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            
        asyncio.run(run_fuzzing())
        
    except Exception as e:
        logger.error(f"Fuzzing failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 