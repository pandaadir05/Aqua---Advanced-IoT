"""
Web interface for Aqua IoT Security Scanner.
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import uvicorn
import os

# Get the directory of the current file (app.py)
BASE_DIR = Path(__file__).parent.absolute()
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Create static and templates directories if they don't exist
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

# Create app
app = FastAPI(
    title="Aqua IoT Security Scanner",
    description="Advanced IoT security analysis and monitoring platform",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Set up templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Define routes
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the main dashboard page."""
    return templates.TemplateResponse("index.html", {"request": request, "active_page": "dashboard"})

@app.get("/devices", response_class=HTMLResponse)
async def devices_page(request: Request):
    """Render the devices page."""
    return templates.TemplateResponse("devices.html", {"request": request, "active_page": "devices"})

@app.get("/vulnerabilities", response_class=HTMLResponse)
async def vulnerabilities_page(request: Request):
    """Render the vulnerabilities page."""
    return templates.TemplateResponse("vulnerabilities.html", {"request": request, "active_page": "vulnerabilities"})

@app.get("/reports", response_class=HTMLResponse)
async def reports_page(request: Request):
    """Render the reports page."""
    return templates.TemplateResponse("reports.html", {"request": request, "active_page": "reports"})

@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """Render the settings page."""
    return templates.TemplateResponse("settings.html", {"request": request, "active_page": "settings"})

@app.get("/live-activity", response_class=HTMLResponse)
async def live_activity_page(request: Request):
    """Render the live activity monitoring page."""
    return templates.TemplateResponse("live-activity.html", {"request": request, "active_page": "live-activity"})

@app.get("/alerts", response_class=HTMLResponse)
async def alerts_page(request: Request):
    """Render the alerts page."""
    return templates.TemplateResponse("alerts.html", {"request": request, "active_page": "alerts"})

@app.get("/help", response_class=HTMLResponse)
async def help_page(request: Request):
    """Render the help and support page."""
    return templates.TemplateResponse("help.html", {"request": request, "active_page": "help"})

# API endpoints
@app.get("/api/devices")
async def get_devices():
    """Get all devices."""
    return [
        {"id": "dev001", "ip": "192.168.1.101", "type": "Camera", "manufacturer": "Hikvision", "risk_score": 87, "vulnerabilities": 5},
        {"id": "dev002", "ip": "192.168.1.102", "type": "Smart Speaker", "manufacturer": "Amazon", "risk_score": 45, "vulnerabilities": 2},
        {"id": "dev003", "ip": "192.168.1.103", "type": "Thermostat", "manufacturer": "Nest", "risk_score": 32, "vulnerabilities": 1},
        {"id": "dev004", "ip": "192.168.1.104", "type": "Router", "manufacturer": "Cisco", "risk_score": 76, "vulnerabilities": 4},
        {"id": "dev005", "ip": "192.168.1.105", "type": "Smart Lock", "manufacturer": "August", "risk_score": 65, "vulnerabilities": 3},
    ]

if __name__ == "__main__":
    print(f"Starting Aqua IoT Security Platform web interface...")
    print(f"Static directory: {STATIC_DIR}")
    print(f"Template directory: {TEMPLATES_DIR}")
    print(f"Access the web interface at http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
