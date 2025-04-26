"""
Vulnerability Analysis Module for Aqua.
"""

from typing import Dict, List, Optional
from datetime import datetime
from loguru import logger
from rich.console import Console
from rich.table import Table

console = Console()

class VulnerabilityAnalyzer:
    """Class for analyzing vulnerabilities in scan results."""
    
    def __init__(self):
        self.console = Console()
        
    def analyze_scan_results(self, scan_results: Dict) -> Dict:
        """Analyze scan results and generate vulnerability report."""
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "target": scan_results.get("target", "Unknown"),
            "vulnerabilities": [],
            "recommendations": []
        }
        
        # Analyze each port
        for port in scan_results.get("ports", []):
            if port.get("status") == "Open":
                vulnerability = self._analyze_port(port)
                if vulnerability:
                    analysis["vulnerabilities"].append(vulnerability)
                    analysis["recommendations"].extend(
                        self._generate_recommendations(vulnerability)
                    )
                    
        return analysis
        
    def _analyze_port(self, port: Dict) -> Optional[Dict]:
        """Analyze a single port for vulnerabilities."""
        if not port.get("service"):
            return None
            
        vulnerability = {
            "port": port["port"],
            "service": port["service"],
            "severity": "Unknown",
            "description": "",
            "cve_ids": []
        }
        
        # Add your vulnerability analysis logic here
        # This is a placeholder implementation
        if port["service"] == "SSH":
            vulnerability.update({
                "severity": "High",
                "description": "SSH service detected - check for weak passwords and outdated versions"
            })
        elif port["service"] == "HTTP":
            vulnerability.update({
                "severity": "Medium",
                "description": "HTTP service detected - check for outdated web server versions"
            })
            
        return vulnerability
        
    def _generate_recommendations(self, vulnerability: Dict) -> List[Dict]:
        """Generate recommendations based on vulnerability."""
        recommendations = []
        
        if vulnerability["service"] == "SSH":
            recommendations.append({
                "action": "Implement strong password policy",
                "priority": "High"
            })
            recommendations.append({
                "action": "Update SSH to latest version",
                "priority": "High"
            })
        elif vulnerability["service"] == "HTTP":
            recommendations.append({
                "action": "Update web server to latest version",
                "priority": "Medium"
            })
            
        return recommendations
        
    def display_analysis(self, analysis: Dict):
        """Display analysis results in console."""
        # Display vulnerabilities
        vuln_table = Table(show_header=True, header_style="bold magenta")
        vuln_table.add_column("Port", style="cyan")
        vuln_table.add_column("Service", style="green")
        vuln_table.add_column("Severity", style="yellow")
        vuln_table.add_column("Description", style="red")
        
        for vuln in analysis["vulnerabilities"]:
            vuln_table.add_row(
                str(vuln["port"]),
                vuln["service"],
                vuln["severity"],
                vuln["description"]
            )
            
        console.print("\n[bold]Vulnerabilities Found:[/bold]")
        console.print(vuln_table)
        
        # Display recommendations
        rec_table = Table(show_header=True, header_style="bold magenta")
        rec_table.add_column("Action", style="green")
        rec_table.add_column("Priority", style="yellow")
        
        for rec in analysis["recommendations"]:
            rec_table.add_row(rec["action"], rec["priority"])
            
        console.print("\n[bold]Recommendations:[/bold]")
        console.print(rec_table) 