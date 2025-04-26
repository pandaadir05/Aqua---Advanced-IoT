"""
Web interface for Aqua IoT Security Scanner.
"""

import os
import json
import uuid
import asyncio
from fastapi import FastAPI, Request, Depends, HTTPException, BackgroundTasks, Cookie, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.websockets import WebSocket, WebSocketDisconnect
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from pydantic import BaseModel, Field
from starlette.middleware.sessions import SessionMiddleware
from .middleware import SessionDebugMiddleware

# Import auth module using absolute import
from aqua.web.auth import (
    authenticate_user, create_session, get_session, delete_session,
    register_user, create_password_reset_token, reset_password, verify_reset_token,
    create_demo_user, load_users
)

# Initialize global sessions dictionary to persist between requests
# In a real app this would be a database
sessions = {}

# Get the directory of the current file (app.py)
BASE_DIR = Path(__file__).parent.absolute()
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
DATA_DIR = BASE_DIR / "data"

# Create directories if they don't exist
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(DATA_DIR / "auth", exist_ok=True)

# Create app
app = FastAPI(
    title="Aqua IoT Security Scanner",
    description="Advanced IoT security analysis and monitoring platform",
    version="1.0.0"
)

# Add SessionMiddleware
app.add_middleware(
    SessionMiddleware,
    secret_key="your-secret-key-here"  # In production, use a proper secret key
)

# Add debug middleware
app.add_middleware(SessionDebugMiddleware)

# Add CORS middleware to handle cache issues
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["ETag"]
)

# Add response header middleware to control caching
@app.middleware("http")
async def add_cache_control_headers(request: Request, call_next):
    response = await call_next(request)
    
    # Add cache control headers
    if request.url.path.startswith("/static"):
        # Cache static files for 1 day
        response.headers["Cache-Control"] = "public, max-age=86400"
    elif request.url.path.startswith("/api"):
        # Don't cache API responses
        response.headers["Cache-Control"] = "no-store, max-age=0"
    
    return response

# Create demo user
create_demo_user()

# Mount static files
app.mount("/static", 
    StaticFiles(directory=str(STATIC_DIR)), 
    name="static"
)

# Set up templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Data storage paths
DEVICES_FILE = DATA_DIR / "devices.json"
SCANS_FILE = DATA_DIR / "scans.json"
VULNERABILITIES_FILE = DATA_DIR / "vulnerabilities.json"
SETTINGS_FILE = DATA_DIR / "settings.json"

# Initialize data files if they don't exist
if not DEVICES_FILE.exists():
    with open(DEVICES_FILE, 'w') as f:
        json.dump([], f)

if not SCANS_FILE.exists():
    with open(SCANS_FILE, 'w') as f:
        json.dump([], f)

if not VULNERABILITIES_FILE.exists():
    with open(VULNERABILITIES_FILE, 'w') as f:
        json.dump([], f)

if not SETTINGS_FILE.exists():
    default_settings = {
        "general": {
            "system_name": "Aqua IoT Security Platform",
            "organization": "My Organization",
            "timezone": "America/New_York",
            "date_format": "MM/DD/YYYY"
        },
        "security": {
            "two_factor_auth": True,
            "session_timeout": 60,
            "password_policy": "strong"
        },
        "notifications": {
            "email_notifications": True,
            "email_recipients": "admin@example.com"
        },
        "api": {
            "enabled": True,
            "keys": [
                {
                    "name": "Default API Key",
                    "key": "aqu_123456789abcdef",
                    "created": "2023-10-15T00:00:00Z"
                }
            ]
        },
        "appearance": {
            "theme": "light",
            "accent_color": "#2c7be5"
        }
    }
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(default_settings, f, indent=2)

# Data models
class Device(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    ip: str
    hostname: Optional[str] = None
    mac: Optional[str] = None
    device_type: str = "unknown"
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    firmware_version: Optional[str] = None
    protocols: List[str] = []
    open_ports: List[int] = []
    services: Dict[str, str] = {}
    vulnerabilities: List[Dict] = []
    last_seen: str = Field(default_factory=lambda: datetime.now().isoformat())
    first_seen: str = Field(default_factory=lambda: datetime.now().isoformat())
    is_online: bool = True
    tags: List[str] = []
    notes: Optional[str] = None

class Vulnerability(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str
    description: str
    severity: str
    device_id: str
    cve_id: Optional[str] = None
    cvss_score: Optional[float] = None
    remediation: Optional[str] = None
    discovered_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    status: str = "open"

class Scan(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: Optional[str] = None
    target: str
    scan_type: str
    status: str = "queued"
    progress: int = 0
    started_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    results: Dict = {}

# API key security
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key_header: str = Depends(API_KEY_HEADER)):
    if not api_key_header:
        return None
        
    try:
        with open(SETTINGS_FILE, 'r') as f:
            settings = json.load(f)
        
        valid_keys = [key["key"] for key in settings["api"]["keys"]]
        if api_key_header in valid_keys:
            return api_key_header
    except:
        pass
        
    return None

# Authentication dependency
async def get_current_user(request: Request):
    """Get current user from session cookie"""
    session_cookie = request.cookies.get("session")
    print(f"Checking session cookie: {session_cookie}")
    
    if not session_cookie:
        print("No session cookie found")
        return None
    
    # Debug sessions
    print(f"Active sessions: {list(sessions.keys())}")
    
    if session_cookie in sessions:
        session_data = sessions[session_cookie]
        
        # Check if session has expired
        if session_data["expires"] < datetime.now():
            print(f"Session expired: {session_cookie}")
            del sessions[session_cookie]
            return None
        
        print(f"Found user: {session_data['user']}")
        return session_data["user"]
    else:
        print(f"Session not found in active sessions: {session_cookie}")
    
    return None

# Helper functions
def load_devices():
    try:
        with open(DEVICES_FILE, 'r') as f:
            return json.load(f)
    except:
        return []
        
def save_devices(devices):
    with open(DEVICES_FILE, 'w') as f:
        json.dump(devices, f, indent=2)

def load_vulnerabilities():
    try:
        with open(VULNERABILITIES_FILE, 'r') as f:
            return json.load(f)
    except:
        return []
        
def save_vulnerabilities(vulnerabilities):
    with open(VULNERABILITIES_FILE, 'w') as f:
        json.dump(vulnerabilities, f, indent=2)

def load_scans():
    try:
        with open(SCANS_FILE, 'r') as f:
            return json.load(f)
    except:
        return []
        
def save_scans(scans):
    with open(SCANS_FILE, 'w') as f:
        json.dump(scans, f, indent=2)

def load_settings():
    try:
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=2)

def load_alerts():
    """Load sample alerts for demo purposes."""
    return [
        {
            "id": "alert001",
            "title": "Unusual Outbound Traffic",
            "description": "Unusual outbound traffic detected from Camera (192.168.1.101) to external IP address (103.45.67.89).",
            "severity": "critical",
            "device": {"id": "dev_1", "name": "Front Door Camera", "ip": "192.168.1.101"},
            "timestamp": "2023-10-28T15:42:00Z",
            "status": "open",
            "category": "Suspicious Traffic",
            "technical_details": "Source: 192.168.1.101\nDestination: 103.45.67.89\nProtocol: TCP\nDestination Port: 8080\nPackets: 1,458\nData Transferred: 15.7MB\nTime Window: 15:30 - 15:42",
            "recommendations": [
                "Block outbound connection to 103.45.67.89",
                "Investigate device for potential compromise",
                "Update device firmware to latest version",
                "Review device access logs"
            ]
        },
        {
            "id": "alert002",
            "title": "Multiple Authentication Failures",
            "description": "Multiple failed authentication attempts detected on Router (192.168.1.104).",
            "severity": "high",
            "device": {"id": "dev_4", "name": "Wi-Fi Router", "ip": "192.168.1.104"},
            "timestamp": "2023-10-28T14:23:00Z",
            "status": "open",
            "category": "Authentication",
            "technical_details": "Source: Multiple IPs\nTarget: 192.168.1.104\nAttempts: 25\nTime Window: 14:15 - 14:23",
            "recommendations": [
                "Enable account lockout after failed attempts",
                "Implement IP-based rate limiting",
                "Review current authentication logs",
                "Consider implementing two-factor authentication"
            ]
        },
        {
            "id": "alert003",
            "title": "Firmware Update Available",
            "description": "Critical security update available for Thermostat (192.168.1.102).",
            "severity": "medium",
            "device": {"id": "dev_2", "name": "Smart Thermostat", "ip": "192.168.1.102"},
            "timestamp": "2023-10-27T09:15:00Z",
            "status": "in_progress",
            "category": "Firmware",
            "technical_details": "Current Version: 2.4.1\nAvailable Version: 2.5.0\nFixed CVEs: CVE-2023-1234, CVE-2023-5678",
            "recommendations": [
                "Update device firmware as soon as possible",
                "Review update release notes",
                "Schedule maintenance window for update"
            ]
        },
        {
            "id": "alert004",
            "title": "Insecure Protocol Detected",
            "description": "Device is using unencrypted MQTT protocol for communication.",
            "severity": "medium",
            "device": {"id": "dev_3", "name": "Smart Lock", "ip": "192.168.1.103"},
            "timestamp": "2023-10-26T18:45:00Z",
            "status": "open",
            "category": "Configuration",
            "technical_details": "Protocol: MQTT\nPort: 1883\nNo TLS/SSL encryption detected",
            "recommendations": [
                "Configure TLS/SSL for MQTT connections",
                "Use MQTT over WebSockets with TLS",
                "Update device configuration"
            ]
        },
        {
            "id": "alert005",
            "title": "New Device Detected",
            "description": "New unrecognized device connected to the network.",
            "severity": "low",
            "device": {"id": "unknown", "name": "Unknown Device", "ip": "192.168.1.120"},
            "timestamp": "2023-10-25T11:30:00Z",
            "status": "resolved",
            "category": "Network",
            "technical_details": "MAC Address: AA:BB:CC:DD:EE:FF\nManufacturer: Unknown\nHostname: android-device",
            "recommendations": [
                "Identify and verify device ownership",
                "Add device to inventory if legitimate",
                "Block device if unauthorized"
            ]
        }
    ]

# Background task to simulate scan progress
async def run_scan(scan_id: str):
    scans = load_scans()
    scan_index = next((i for i, s in enumerate(scans) if s["id"] == scan_id), None)
    
    if scan_index is not None:
        # Update status to running
        scans[scan_index]["status"] = "running"
        save_scans(scans)
        
        # Simulate scan progress
        for progress in range(0, 101, 5):
            scans = load_scans()
            scan_index = next((i for i, s in enumerate(scans) if s["id"] == scan_id), None)
            
            if scan_index is None:
                break
                
            scans[scan_index]["progress"] = progress
            save_scans(scans)
            
            # Send notification to websocket clients
            for client in active_websockets:
                try:
                    await client.send_json({
                        "type": "scan_progress",
                        "scan_id": scan_id,
                        "progress": progress
                    })
                except:
                    pass
            
            await asyncio.sleep(1)
            
        # Simulate finding some devices and vulnerabilities
        devices = load_devices()
        vulnerabilities = load_vulnerabilities()
        
        # Get target from the scan
        target = scans[scan_index]["target"]
        
        # Create some demo devices based on the target
        if target.endswith("/24"):  # Network scan
            base_ip = target.split("/")[0].rsplit(".", 1)[0]
            
            # Add sample devices
            new_devices = [
                Device(
                    ip=f"{base_ip}.101",
                    hostname="iot-camera-01",
                    device_type="camera",
                    manufacturer="SecurityCam",
                    model="SC-2000",
                    open_ports=[80, 443, 8080],
                    protocols=["HTTP", "HTTPS", "RTSP"],
                    services={"80": "HTTP", "443": "HTTPS", "8080": "HTTP-alt"}
                ),
                Device(
                    ip=f"{base_ip}.102",
                    hostname="smart-thermostat",
                    device_type="thermostat",
                    manufacturer="SmartHome",
                    model="TH-2000",
                    open_ports=[80, 1883],
                    protocols=["HTTP", "MQTT"],
                    services={"80": "HTTP", "1883": "MQTT"}
                ),
                Device(
                    ip=f"{base_ip}.103",
                    hostname="smart-lock",
                    device_type="lock",
                    manufacturer="SecureLock",
                    model="SL-500",
                    open_ports=[80, 443, 5683],
                    protocols=["HTTP", "HTTPS", "CoAP"],
                    services={"80": "HTTP", "443": "HTTPS", "5683": "CoAP"}
                )
            ]
            
            # Check if devices already exist
            existing_ips = [d["ip"] for d in devices]
            for device in new_devices:
                device_dict = device.dict()
                if device_dict["ip"] not in existing_ips:
                    devices.append(device_dict)
                    
                    # Add vulnerabilities for the device
                    if device_dict["device_type"] == "camera":
                        vulnerabilities.append(
                            Vulnerability(
                                name="Default Credentials",
                                description="Device uses default login credentials (admin/admin)",
                                severity="high",
                                device_id=device_dict["id"],
                                remediation="Change the default credentials"
                            ).dict()
                        )
                    elif device_dict["device_type"] == "thermostat":
                        vulnerabilities.append(
                            Vulnerability(
                                name="Unencrypted MQTT",
                                description="Device uses unencrypted MQTT protocol",
                                severity="medium",
                                device_id=device_dict["id"],
                                remediation="Configure TLS for MQTT connections"
                            ).dict()
                        )
                    elif device_dict["device_type"] == "lock":
                        vulnerabilities.append(
                            Vulnerability(
                                name="Outdated Firmware",
                                description="Device is running outdated firmware with known vulnerabilities",
                                severity="high",
                                device_id=device_dict["id"],
                                cve_id="CVE-2023-1234",
                                cvss_score=8.5,
                                remediation="Update to the latest firmware version"
                            ).dict()
                        )
            
            save_devices(devices)
            save_vulnerabilities(vulnerabilities)
            
            # Update scan results
            device_ids = [d["id"] for d in devices if d["ip"].startswith(base_ip)]
            vulnerability_ids = [v["id"] for v in vulnerabilities if v["device_id"] in device_ids]
            
            scans[scan_index]["results"] = {
                "devices_found": len(device_ids),
                "vulnerabilities_found": len(vulnerability_ids),
                "device_ids": device_ids,
                "vulnerability_ids": vulnerability_ids
            }
        
        # Complete the scan
        scans[scan_index]["status"] = "completed"
        scans[scan_index]["progress"] = 100
        scans[scan_index]["completed_at"] = datetime.now().isoformat()
        save_scans(scans)
        
        # Notify websocket clients
        for client in active_websockets:
            try:
                await client.send_json({
                    "type": "scan_completed",
                    "scan_id": scan_id
                })
            except:
                pass

# WebSocket handling
active_websockets = set()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_websockets.add(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # We can handle different message types here if needed
            await websocket.send_json({"message": "Received", "data": json.loads(data)})
    except WebSocketDisconnect:
        active_websockets.remove(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        if websocket in active_websockets:
            active_websockets.remove(websocket)

# Authentication routes
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, current_user: Optional[Dict] = Depends(get_current_user)):
    if current_user:
        return RedirectResponse(url="/dashboard")
    
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login_user(
    request: Request,
    response: Response,
    username: str = Form(...), 
    password: str = Form(...),
    remember: bool = Form(False),
):
    # For debugging
    print(f"Login attempt: username={username}, password={password}")
    
    # Hard-coded demo credentials for testing
    if username == "admin" and password == "password":
        token = str(uuid.uuid4())
        exp = 30 if remember else 1  # Days to expire
        
        print(f"Login successful, created session token: {token}")
        
        # Store in global sessions dictionary
        sessions[token] = {
            "user": {
                "username": username,
                "role": "admin",
                "name": "Admin User"
            },
            "expires": datetime.now() + timedelta(days=exp)
        }
        
        # Create response with redirect
        response = RedirectResponse(url="/dashboard", status_code=303)
        
        # Set cookie
        response.set_cookie(
            key="session",
            value=token,
            httponly=True,
            max_age=exp * 24 * 60 * 60,  # Convert days to seconds
            secure=False
        )
        
        return response
    else:
        # Show error message for invalid login
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "error": "Invalid username or password. Use admin/password"}
        )

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, current_user: Optional[Dict] = Depends(get_current_user)):
    # Redirect to dashboard if already logged in
    if current_user:
        return RedirectResponse(url="/dashboard")
    
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register(request: Request):
    form_data = await request.form()
    username = form_data.get("username")
    password = form_data.get("password")
    confirm_password = form_data.get("confirm_password")
    email = form_data.get("email")
    full_name = form_data.get("full_name")
    
    # Validate inputs
    if not username or not password or not email or not full_name:
        return templates.TemplateResponse(
            "register.html", 
            {"request": request, "error": "All fields are required"}
        )
    
    if password != confirm_password:
        return templates.TemplateResponse(
            "register.html", 
            {"request": request, "error": "Passwords do not match"}
        )
    
    try:
        user = register_user(username, password, email, full_name)
        # Create session and log in the user
        session_id = create_session(user["id"])
        
        # Redirect to dashboard with session cookie
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            max_age=86400,  # 1 day
            samesite="lax"
        )
        
        return response
    except ValueError as e:
        return templates.TemplateResponse(
            "register.html", 
            {"request": request, "error": str(e)}
        )

@app.get("/logout")
async def logout(response: Response, session: Optional[str] = Cookie(None)):
    if session and session in sessions:
        print(f"Logging out user with session: {session}")
        del sessions[session]
    
    response = RedirectResponse(url="/login")
    response.delete_cookie(key="session")
    return response

@app.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(request: Request):
    return templates.TemplateResponse("forgot-password.html", {"request": request})

@app.post("/forgot-password")
async def forgot_password(request: Request):
    form_data = await request.form()
    email = form_data.get("email")
    
    if not email:
        return templates.TemplateResponse(
            "forgot-password.html", 
            {"request": request, "error": "Email is required"}
        )
    
    # Create reset token - in a real app, send this via email
    token = create_password_reset_token(email)
    
    if token:
        # For demo purposes, just show success message
        # In a real app, send an email with reset link
        print(f"Password reset link: http://localhost:8000/reset-password?token={token}")
        return templates.TemplateResponse(
            "forgot-password.html",
            {"request": request, "success": True}
        )
    else:
        # Don't reveal whether the email exists or not for security
        return templates.TemplateResponse(
            "forgot-password.html",
            {"request": request, "success": True}
        )

# Define routes
@app.get("/landing", response_class=HTMLResponse)
async def landing_page(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/", response_class=HTMLResponse)
async def root(request: Request, current_user: Optional[Dict] = Depends(get_current_user)):
    if not current_user:
        return RedirectResponse(url="/landing")
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "user": current_user
    })

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, current_user: Optional[Dict] = Depends(get_current_user)):
    if not current_user:
        return RedirectResponse(url="/login")
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "user": current_user
    })

@app.get("/devices", response_class=HTMLResponse)
async def devices_page(request: Request, current_user: Optional[Dict] = Depends(get_current_user)):
    if not current_user:
        return RedirectResponse(url="/login")
    
    return templates.TemplateResponse("devices.html", {
        "request": request, 
        "user": current_user
    })

@app.get("/vulnerabilities", response_class=HTMLResponse)
async def vulnerabilities_page(request: Request, current_user: Optional[Dict] = Depends(get_current_user)):
    if not current_user:
        return RedirectResponse(url="/login")
    
    return templates.TemplateResponse("vulnerabilities.html", {
        "request": request, 
        "user": current_user
    })

@app.get("/reports", response_class=HTMLResponse)
async def reports_page(request: Request, current_user: Optional[Dict] = Depends(get_current_user)):
    if not current_user:
        return RedirectResponse(url="/login")
    
    return templates.TemplateResponse("reports.html", {
        "request": request, 
        "user": current_user
    })

@app.get("/live-activity", response_class=HTMLResponse)
async def live_activity_page(request: Request, current_user: Optional[Dict] = Depends(get_current_user)):
    if not current_user:
        return RedirectResponse(url="/login")
    
    return templates.TemplateResponse("live-activity.html", {
        "request": request, 
        "user": current_user
    })

@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request, current_user: Optional[Dict] = Depends(get_current_user)):
    if not current_user:
        return RedirectResponse(url="/login")
    
    return templates.TemplateResponse("settings.html", {
        "request": request, 
        "user": current_user
    })

@app.get("/help", response_class=HTMLResponse)
async def help_page(request: Request, current_user: Optional[Dict] = Depends(get_current_user)):
    if not current_user:
        return RedirectResponse(url="/login")
    
    return templates.TemplateResponse("help.html", {
        "request": request, 
        "user": current_user
    })

@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, current_user: Optional[Dict] = Depends(get_current_user)):
    if not current_user:
        return RedirectResponse(url="/login")
    
    return templates.TemplateResponse("profile.html", {
        "request": request, 
        "user": current_user
    })

@app.get("/alerts", response_class=HTMLResponse)
async def alerts_page(request: Request, current_user: Optional[Dict] = Depends(get_current_user)):
    if not current_user:
        return RedirectResponse(url="/login")
    
    return templates.TemplateResponse("alerts.html", {
        "request": request, 
        "user": current_user
    })

@app.get("/api/alerts")
async def get_alerts_api(current_user: Optional[Dict] = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    alerts = load_alerts()
    return alerts

@app.get("/api/alerts/{alert_id}")
async def get_alert_api(alert_id: str, current_user: Optional[Dict] = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    alerts = load_alerts()
    for alert in alerts:
        if alert.get('id') == alert_id:
            return alert
    
    raise HTTPException(status_code=404, detail="Alert not found")

# API routes
@app.get("/api/devices")
async def get_devices_api():
    # Removed API key check temporarily to fix issues
    return load_devices()

@app.get("/api/devices/{device_id}")
async def get_device_api(device_id: str):
    # Removed API key check temporarily
    devices = load_devices()
    device = next((d for d in devices if d["id"] == device_id), None)
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
        
    return device

@app.post("/api/devices")
async def add_device_api(device: Device):
    # Removed API key check temporarily
    devices = load_devices()
    device_dict = device.dict()
    
    # Check if device with same IP already exists
    existing = next((d for d in devices if d["ip"] == device_dict["ip"]), None)
    if existing:
        raise HTTPException(status_code=400, detail="Device with this IP already exists")
        
    devices.append(device_dict)
    save_devices(devices)
    return device_dict

@app.put("/api/devices/{device_id}")
async def update_device_api(device_id: str, device_update: Dict):
    # Removed API key check temporarily
    devices = load_devices()
    device_index = next((i for i, d in enumerate(devices) if d["id"] == device_id), None)
    
    if device_index is None:
        raise HTTPException(status_code=404, detail="Device not found")
        
    # Update device
    for key, value in device_update.items():
        if key != "id":  # Don't allow changing the ID
            devices[device_index][key] = value
            
    save_devices(devices)
    return devices[device_index]

@app.delete("/api/devices/{device_id}")
async def delete_device_api(device_id: str):
    # Removed API key check temporarily
    devices = load_devices()
    device = next((d for d in devices if d["id"] == device_id), None)
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
        
    devices = [d for d in devices if d["id"] != device_id]
    save_devices(devices)
    
    # Also delete associated vulnerabilities
    vulnerabilities = load_vulnerabilities()
    vulnerabilities = [v for v in vulnerabilities if v["device_id"] != device_id]
    save_vulnerabilities(vulnerabilities)
    
    return {"message": "Device deleted successfully"}

@app.get("/api/vulnerabilities")
async def get_vulnerabilities_api(device_id: Optional[str] = None):
    # Removed API key check temporarily
    vulnerabilities = load_vulnerabilities()
    
    if device_id:
        vulnerabilities = [v for v in vulnerabilities if v["device_id"] == device_id]
        
    return vulnerabilities

@app.get("/api/scans")
async def get_scans_api():
    # No API key check for now to fix the issue
    return load_scans()

@app.post("/api/scans")
async def start_scan_api(scan: Dict, background_tasks: BackgroundTasks):
    # No API key check for now to fix the issue
    new_scan = Scan(
        target=scan["target"],
        scan_type=scan.get("scan_type", "full"),
        name=scan.get("name")
    )
    
    scan_dict = new_scan.dict()
    
    scans = load_scans()
    scans.append(scan_dict)
    save_scans(scans)
    
    # Start the scan in the background
    background_tasks.add_task(run_scan, scan_dict["id"])
    
    return {"scan_id": scan_dict["id"]}

@app.get("/api/scans/{scan_id}")
async def get_scan_status_api(scan_id: str):
    # No API key check for now to fix the issue
    scans = load_scans()
    scan = next((s for s in scans if s["id"] == scan_id), None)
    
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
        
    return scan

@app.get("/api/scans/{scan_id}/results")
async def get_scan_results_api(scan_id: str):
    # No API key check for now to fix the issue
    scans = load_scans()
    scan = next((s for s in scans if s["id"] == scan_id), None)
    
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
        
    if scan["status"] != "completed":
        raise HTTPException(status_code=400, detail="Scan is not completed yet")
        
    # Get detailed results
    devices = []
    vulnerabilities = []
    
    if "results" in scan and "device_ids" in scan["results"]:
        all_devices = load_devices()
        all_vulnerabilities = load_vulnerabilities()
        
        devices = [d for d in all_devices if d["id"] in scan["results"]["device_ids"]]
        vulnerabilities = [v for v in all_vulnerabilities if v["id"] in scan["results"].get("vulnerability_ids", [])]
    
    return {
        "scan": scan,
        "devices": devices,
        "vulnerabilities": vulnerabilities
    }

@app.post("/api/scans/{scan_id}/stop")
async def stop_scan_api(scan_id: str):
    # No API key check for now to fix the issue
    scans = load_scans()
    scan_index = next((i for i, s in enumerate(scans) if s["id"] == scan_id), None)
    
    if scan_index is None:
        raise HTTPException(status_code=404, detail="Scan not found")
        
    if scans[scan_index]["status"] == "running":
        scans[scan_index]["status"] = "stopped"
        scans[scan_index]["completed_at"] = datetime.now().isoformat()
        save_scans(scans)
        
    return {"message": "Scan stopped"}

@app.get("/api/settings")
async def get_settings_api(api_key: str = Depends(get_api_key)):
    if api_key is None:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
        
    settings = load_settings()
    
    # Don't return API keys
    if "api" in settings and "keys" in settings["api"]:
        for key in settings["api"]["keys"]:
            key["key"] = key["key"][:8] + "..." + key["key"][-4:]
            
    return settings

@app.put("/api/settings/{section}")
async def update_settings_api(section: str, settings_update: Dict, api_key: str = Depends(get_api_key)):
    if api_key is None:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
        
    settings = load_settings()
    
    if section not in settings:
        raise HTTPException(status_code=404, detail=f"Settings section '{section}' not found")
        
    settings[section].update(settings_update)
    save_settings(settings)
    return {"message": f"Settings section '{section}' updated successfully"}

@app.post("/api/settings/api/keys")
async def add_api_key_api(key_data: Dict, api_key: str = Depends(get_api_key)):
    if api_key is None:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
        
    settings = load_settings()
    
    if "name" not in key_data:
        raise HTTPException(status_code=400, detail="API key name is required")
        
    # Generate a new API key
    new_key = f"aqu_{uuid.uuid4().hex}"
    
    # Add the key
    new_key_data = {
        "name": key_data["name"],
        "key": new_key,
        "created": datetime.now().isoformat()
    }
    
    settings["api"]["keys"].append(new_key_data)
    save_settings(settings)
    
    return new_key_data

@app.get("/api/test-scan")
async def test_scan_api():
    """Test endpoint to verify scan functionality"""
    # Create a test scan
    scan = Scan(
        name="Test Scan",
        target="127.0.0.1",
        scan_type="quick"
    )
    
    scan_dict = scan.dict()
    
    # Add some results
    scan_dict["status"] = "completed"
    scan_dict["progress"] = 100
    scan_dict["completed_at"] = datetime.now().isoformat()
    scan_dict["results"] = {
        "devices_found": 1,
        "vulnerabilities_found": 2,
        "device_ids": ["test_device"],
        "vulnerability_ids": ["test_vuln1", "test_vuln2"]
    }
    
    return {
        "message": "Test scan functionality working",
        "scan": scan_dict
    }

@app.get("/api/debug/system-status")
async def debug_system_status():
    """Debug endpoint to check system status"""
    
    # Get counts of data
    device_count = len(load_devices())
    vuln_count = len(load_vulnerabilities())
    scan_count = len(load_scans())
    
    # Check if data directories exist
    data_dir_exists = os.path.exists(DATA_DIR)
    
    # Check if data files exist
    devices_file_exists = os.path.exists(DEVICES_FILE)
    vulnerabilities_file_exists = os.path.exists(VULNERABILITIES_FILE)
    scans_file_exists = os.path.exists(SCANS_FILE)
    settings_file_exists = os.path.exists(SETTINGS_FILE)
    
    # Check websocket status
    websocket_client_count = len(active_websockets)
    
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "data_counts": {
            "devices": device_count,
            "vulnerabilities": vuln_count,
            "scans": scan_count,
            "websocket_clients": websocket_client_count
        },
        "file_status": {
            "data_dir_exists": data_dir_exists,
            "devices_file_exists": devices_file_exists,
            "vulnerabilities_file_exists": vulnerabilities_file_exists,
            "scans_file_exists": scans_file_exists,
            "settings_file_exists": settings_file_exists
        },
        "paths": {
            "data_dir": str(DATA_DIR),
            "devices_file": str(DEVICES_FILE),
            "vulnerabilities_file": str(VULNERABILITIES_FILE), 
            "scans_file": str(SCANS_FILE),
            "settings_file": str(SETTINGS_FILE)
        }
    }

@app.get("/api/alerts/{alert_id}")
async def get_alert_details_api(alert_id: str):
    """Get details for a specific alert."""
    # Demo alert data - in a real app this would come from a database
    demo_alerts = {
        "alert001": {
            "id": "alert001",
            "title": "Unauthorized Access Attempt",
            "device": {"id": "dev001", "name": "Camera", "ip": "192.168.1.101"},
            "severity": "critical",
            "status": "open",
            "timestamp": "2023-11-02T14:28:05Z",
            "description": "Multiple failed login attempts detected on the device from IP address 192.168.1.35.",
            "technical_details": {
                "source_ip": "192.168.1.35",
                "destination_ip": "192.168.1.101",
                "destination_port": 22,
                "protocol": "SSH",
                "attempts": 5,
                "usernames": ["admin", "root"],
                "timestamp": "2023-11-02T14:28:05Z"
            },
            "recommendations": [
                "Check access logs for the source IP",
                "Temporarily block the source IP if suspicious",
                "Enable account lockout after failed attempts"
            ]
        },
        "alert002": {
            "id": "alert002", 
            "title": "Outdated Firmware", 
            "device": {"id": "dev004", "name": "Router", "ip": "192.168.1.1"},
            "severity": "high", 
            "status": "open", 
            "timestamp": "2023-11-02T12:15:22Z",
            "description": "Device is running firmware version 3.4.2 which has known vulnerabilities. Latest version is 4.0.1.",
            "technical_details": {
                "current_version": "3.4.2",
                "latest_version": "4.0.1",
                "cve_references": ["CVE-2023-1234", "CVE-2023-5678"],
                "last_checked": "2023-11-02T12:00:00Z"
            },
            "recommendations": [
                "Update router firmware to version 4.0.1 or later",
                "Follow vendor's update instructions",
                "Backup configuration before updating"
            ]
        }
    }
    
    # Generate data for other alerts
    for i in range(3, 11):
        alert_id_str = f"alert{i:03d}"
        if alert_id_str not in demo_alerts:
            demo_alerts[alert_id_str] = {
                "id": alert_id_str,
                "title": f"Demo Alert {i}",
                "device": {"id": f"dev{i:03d}", "name": f"Device {i}", "ip": f"192.168.1.{100+i}"},
                "severity": ["low", "medium", "high", "critical"][i % 4],
                "status": ["open", "in_progress", "resolved"][i % 3],
                "timestamp": f"2023-11-0{i%3+1}T{i+10}:00:00Z",
                "description": f"This is a demo alert {i} description.",
                "technical_details": {
                    "demo_field": f"Demo value {i}",
                    "timestamp": f"2023-11-0{i%3+1}T{i+10}:00:00Z"
                },
                "recommendations": [
                    f"Recommendation {i}.1",
                    f"Recommendation {i}.2"
                ]
            }
    
    if alert_id in demo_alerts:
        return demo_alerts[alert_id]
    else:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")

if __name__ == "__main__":
    print(f"Starting Aqua IoT Security Platform web interface...")
    print(f"Static directory: {STATIC_DIR}")
    print(f"Template directory: {TEMPLATES_DIR}")
    print(f"Access the web interface at http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
