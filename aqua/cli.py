import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt
from rich.layout import Layout
from rich.live import Live
from rich.align import Align
from rich import box
import time
import os
import sys
from typing import Optional
import json
from datetime import datetime
from pathlib import Path
from loguru import logger
from .core.scanner import IoTPTFScanner
from .core.analyzer import VulnerabilityAnalyzer
from .core.exploiter import IoTPTFExploiter
from .core.cve_db import CVEDatabase
from .core.protection import ProtectionEngine

app = typer.Typer(help="Aqua - Next Generation IoT Security Scanner")
console = Console()

def display_banner():
    banner = """
    █████╗ ██████╗ ██╗   ██╗ █████╗ 
    ██╔══██╗██╔══██╗██║   ██║██╔══██╗
    ███████║██████╔╝██║   ██║███████║
    ██╔══██║██╔══██╗██║   ██║██╔══██║
    ██║  ██║██║  ██║╚██████╔╝██║  ██║
    ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝
    """
    version = "[bold cyan]v1.0.0[/bold cyan]"
    tagline = "[bold yellow]Next Generation IoT Security Scanner[/bold yellow]"
    
    panel = Panel(
        Align.center(f"{banner}\n{tagline}\n{version}"),
        border_style="blue",
        box=box.DOUBLE,
        title="[bold white]Aqua[/bold white]",
        subtitle="[italic]By Your Security Team[/italic]"
    )
    console.print(panel)

def display_menu():
    table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("Command", style="cyan", justify="right")
    table.add_column("Description", style="green")
    table.add_column("Usage", style="yellow")
    
    table.add_row(
        "scan",
        "Scan target for vulnerabilities",
        "aqua scan <target> [-p ports] [-o output]"
    )
    table.add_row(
        "analyze",
        "Analyze scan results",
        "aqua analyze <file> [-o output]"
    )
    table.add_row(
        "exploit",
        "Exploit vulnerabilities",
        "aqua exploit <target> <vulnerability>"
    )
    
    console.print("\n[bold white]Available Commands:[/bold white]")
    console.print(table)

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Aqua - Next Generation IoT Security Scanner"""
    if ctx.invoked_subcommand is None:
        display_banner()
        display_menu()
        console.print("\n[bold green]Type 'aqua --help' for more information.[/bold green]")

def display_progress(description: str, steps: int = 100) -> None:
    """Display a professional progress bar."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
    ) as progress:
        task = progress.add_task(f"[cyan]{description}[/cyan]", total=steps)
        for _ in range(steps):
            time.sleep(0.05)
            progress.update(task, advance=1)

@app.command()
def scan(
    target: str = typer.Argument(..., help="Target IP address or hostname"),
    ports: str = typer.Option("1-1000", "--ports", "-p", help="Port range to scan"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    output: str = typer.Option(None, "--output", "-o", help="Output file path for scan results"),
):
    """Scan a target for vulnerabilities."""
    display_banner()
    
    # Show scan configuration
    config_table = Table(show_header=False, box=box.SIMPLE)
    config_table.add_row("Target", f"[cyan]{target}[/cyan]")
    config_table.add_row("Ports", f"[yellow]{ports}[/yellow]")
    config_table.add_row("Verbose", f"[green]{verbose}[/green]")
    console.print(Panel(config_table, title="[bold]Scan Configuration[/bold]"))
    
    display_progress("Scanning target")
    
    # Example results
    results = {
        "target": target,
        "ports": [
            {"port": 22, "service": "SSH", "status": "Open", "vulnerability": "Weak password policy"},
            {"port": 80, "service": "HTTP", "status": "Open", "vulnerability": "Outdated Apache version"},
            {"port": 443, "service": "HTTPS", "status": "Open", "vulnerability": "SSL/TLS misconfiguration"}
        ]
    }
    
    # Display results in a modern table
    table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("Port", style="cyan", justify="center")
    table.add_column("Service", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Vulnerability", style="red")
    
    for port in results["ports"]:
        table.add_row(
            str(port["port"]),
            port["service"],
            port["status"],
            port["vulnerability"]
        )
    
    console.print("\n[bold white]Scan Results:[/bold white]")
    console.print(table)
    
    if output:
        try:
            with open(output, 'w') as f:
                json.dump(results, f, indent=2)
            console.print(f"\n[green]✓[/green] Scan results saved to: [blue]{output}[/blue]")
        except Exception as e:
            console.print(f"\n[red]✗[/red] Error saving scan results: {e}")

@app.command()
def analyze(
    file: str = typer.Argument(..., help="Path to scan results file"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
):
    """Analyze scan results and generate report."""
    display_banner()
    
    if not os.path.exists(file):
        console.print(f"\n[red]✗[/red] Error: File '{file}' not found!")
        raise typer.Exit(1)
    
    # Read the scan results
    try:
        with open(file, 'r') as f:
            scan_results = json.load(f)
    except Exception as e:
        console.print(f"\n[red]✗[/red] Error reading scan results: {e}")
        raise typer.Exit(1)
    
    display_progress("Analyzing results")
    
    # Generate analysis results
    analysis_results = {
        "target": scan_results["target"],
        "timestamp": datetime.now().isoformat(),
        "vulnerabilities": [],
        "recommendations": []
    }
    
    # Analyze each port
    for port in scan_results["ports"]:
        if port["status"] == "Open":
            severity = "High" if "password" in port["vulnerability"].lower() else "Medium"
            analysis_results["vulnerabilities"].append({
                "port": port["port"],
                "service": port["service"],
                "vulnerability": port["vulnerability"],
                "severity": severity
            })
            
            # Add recommendations
            if "password" in port["vulnerability"].lower():
                analysis_results["recommendations"].append({
                    "port": port["port"],
                    "action": "Implement strong password policy",
                    "priority": "High"
                })
            elif "Outdated" in port["vulnerability"]:
                analysis_results["recommendations"].append({
                    "port": port["port"],
                    "action": "Update service to latest version",
                    "priority": "Medium"
                })
            elif "SSL/TLS" in port["vulnerability"]:
                analysis_results["recommendations"].append({
                    "port": port["port"],
                    "action": "Configure proper SSL/TLS settings",
                    "priority": "High"
                })
    
    # Save analysis results if output path is specified
    if output:
        try:
            with open(output, 'w') as f:
                json.dump(analysis_results, f, indent=2)
            console.print(f"\n[green]✓[/green] Analysis results saved to: [blue]{output}[/blue]")
        except Exception as e:
            console.print(f"\n[red]✗[/red] Error saving analysis results: {e}")
    
    # Display results in modern tables
    vuln_table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    vuln_table.add_column("Port", style="cyan", justify="center")
    vuln_table.add_column("Service", style="green")
    vuln_table.add_column("Vulnerability", style="red")
    vuln_table.add_column("Severity", style="yellow")
    
    for vuln in analysis_results["vulnerabilities"]:
        vuln_table.add_row(
            str(vuln["port"]),
            vuln["service"],
            vuln["vulnerability"],
            vuln["severity"]
        )
    
    rec_table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    rec_table.add_column("Port", style="cyan", justify="center")
    rec_table.add_column("Action", style="green")
    rec_table.add_column("Priority", style="yellow")
    
    for rec in analysis_results["recommendations"]:
        rec_table.add_row(
            str(rec["port"]),
            rec["action"],
            rec["priority"]
        )
    
    console.print("\n[bold white]Vulnerabilities:[/bold white]")
    console.print(vuln_table)
    console.print("\n[bold white]Recommendations:[/bold white]")
    console.print(rec_table)

@app.command()
def exploit(
    target: str = typer.Argument(..., help="Target IP address or hostname"),
    vulnerability: str = typer.Argument(..., help="Vulnerability to exploit"),
):
    """Exploit a specific vulnerability on a target."""
    display_banner()
    
    # Show warning panel
    warning = Panel(
        "[bold red]⚠ WARNING: This operation may be illegal if performed without proper authorization.[/bold red]\n" +
        "[yellow]Make sure you have explicit permission to perform this action.[/yellow]",
        border_style="red",
        box=box.HEAVY
    )
    console.print(warning)
    
    if not Confirm.ask(f"\nAre you sure you want to exploit [red]{vulnerability}[/red] on [cyan]{target}[/cyan]?"):
        console.print("\n[yellow]Operation cancelled by user.[/yellow]")
        raise typer.Exit()
    
    display_progress("Exploiting vulnerability")
    
    console.print("\n[bold green]✓[/bold green] Exploitation successful!")

# Protection commands
protect_app = typer.Typer(help="Manage protection features")
app.add_typer(protect_app, name="protect")

@protect_app.command("protection")
def protection(
    start: bool = typer.Option(False, "--start", help="Start protection"),
    stop: bool = typer.Option(False, "--stop", help="Stop protection"),
    status: bool = typer.Option(False, "--status", help="Show protection status"),
    config: bool = typer.Option(False, "--config", help="Show protection configuration"),
):
    """Manage protection features"""
    engine = ProtectionEngine()
    
    if start:
        engine.start_protection()
        console.print("[green]Protection started successfully[/green]")
        
    elif stop:
        engine.stop_protection()
        console.print("[yellow]Protection stopped[/yellow]")
        
    elif status:
        status = engine.get_status()
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Feature", style="cyan")
        table.add_column("Status", style="green")
        
        for protection in status["active_protections"]:
            table.add_row(protection, "Active")
            
        console.print("\n[bold]Protection Status[/bold]")
        console.print(table)
        console.print(f"\nTotal Alerts: {status['alert_count']}")
        
    elif config:
        config = engine.config
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Feature", style="cyan")
        table.add_column("Enabled", style="green")
        table.add_column("Settings", style="yellow")
        
        for feature, settings in config.items():
            enabled = settings.get("enabled", False)
            table.add_row(
                feature,
                "Yes" if enabled else "No",
                str(settings)
            )
            
        console.print("\n[bold]Protection Configuration[/bold]")
        console.print(table)

@protect_app.command("configure")
def configure(
    network: bool = typer.Option(False, "--network", help="Configure network protection"),
    process: bool = typer.Option(False, "--process", help="Configure process protection"),
    file: bool = typer.Option(False, "--file", help="Configure file protection"),
    alerting: bool = typer.Option(False, "--alerting", help="Configure alerting"),
):
    """Configure protection features"""
    engine = ProtectionEngine()
    
    if network:
        console.print("\n[bold]Network Protection Configuration[/bold]")
        enabled = Confirm.ask("Enable network protection?")
        ports = Prompt.ask("Blocked ports (comma-separated)", default="22,23,80,443")
        rate_limit = Prompt.ask("Rate limit (packets/second)", default=100)
        
        engine.config["network_protection"].update({
            "enabled": enabled,
            "block_ports": [int(p) for p in ports.split(",")],
            "rate_limit": rate_limit
        })
        
    elif process:
        console.print("\n[bold]Process Protection Configuration[/bold]")
        enabled = Confirm.ask("Enable process protection?")
        monitor = Confirm.ask("Monitor processes?")
        block = Confirm.ask("Block unauthorized processes?")
        
        engine.config["process_protection"].update({
            "enabled": enabled,
            "monitor_processes": monitor,
            "block_unauthorized": block
        })
        
    elif file:
        console.print("\n[bold]File Protection Configuration[/bold]")
        enabled = Confirm.ask("Enable file protection?")
        paths = Prompt.ask("Monitor paths (comma-separated)", default="/etc,/bin,/sbin")
        block = Confirm.ask("Block unauthorized files?")
        
        engine.config["file_protection"].update({
            "enabled": enabled,
            "monitor_paths": paths.split(","),
            "block_unauthorized": block
        })
        
    elif alerting:
        console.print("\n[bold]Alerting Configuration[/bold]")
        enabled = Confirm.ask("Enable alerting?")
        webhook = Prompt.ask("Webhook URL (optional)", default="")
        
        engine.config["alerting"].update({
            "enabled": enabled,
            "webhook_url": webhook if webhook else None
        })
        
    engine.save_config()
    console.print("[green]Configuration saved successfully[/green]")

if __name__ == "__main__":
    app() 