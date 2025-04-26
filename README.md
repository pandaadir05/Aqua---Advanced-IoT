# Aqua: Advanced IoT Security Analysis Framework

## Overview

Aqua is a comprehensive security framework for Internet of Things (IoT) devices, integrating behavioral analysis, machine learning, and real-time monitoring to address unique security challenges in IoT environments.

## Key Features

- **IoT Device Discovery**: Network scanning, device fingerprinting, service detection
- **Vulnerability Assessment**: Port scanning, credential checking, vulnerability identification
- **Protocol Fuzzing**: Support for HTTP, MQTT, CoAP, and Modbus protocols
- **Behavioral Analysis**: ML-based anomaly detection, traffic analysis
- **Security Monitoring**: Advanced alerting, multiple notification channels
- **Analytics & Reporting**: Statistical analysis, trend detection, multiple export formats

## Installation

```bash
# Using pip
pip install aqua-security

# From source
git clone https://github.com/adir9/aqua-security.git
cd aqua-security
pip install -r requirements.txt
pip install -e .

# Using Docker
docker pull adir9/aqua-security:latest
docker run -p 8000:8000 -v $(pwd)/data:/app/data adir9/aqua-security:latest
```

## Quick Start

### Command Line Interface (CLI)

```bash
# Discover IoT devices
aqua discover 192.168.1.0/24

# Scan a specific device
aqua scan 192.168.1.100

# Protocol fuzzing
aqua fuzz 192.168.1.100 --protocol mqtt

# Comprehensive assessment
aqua assess 192.168.1.0/24 --output report.json
```

### Python API

```python
from aqua.core import IoTPTF
import asyncio

async def run_assessment():
    framework = IoTPTF()
    devices = await framework.discover_devices("192.168.1.0/24")
    print(f"Discovered {len(devices)} devices.")
    
    for device in devices:
        vulnerabilities = await framework.assess_device(device)
        print(f"Found {len(vulnerabilities)} vulnerabilities on {device.ip}")

if __name__ == "__main__":
    asyncio.run(run_assessment())
```

### Web Interface

Start with: `aqua web --port 8000` and access at `http://localhost:8000`

## Project Structure

```
aqua/
├── __init__.py           # Package initialization
├── cli.py                # Command-line interface
├── core/                 # Core framework components
│   ├── analyzer.py       # Vulnerability analysis
│   ├── behavioral.py     # Behavioral analysis with ML
│   ├── device.py         # IoT device models
│   ├── framework.py      # Main framework API
│   ├── reporting.py      # Reporting and analytics
│   ├── scanner.py        # Network and vulnerability scanning
│   └── vulnerability.py  # Vulnerability models
├── modules/              # Feature-specific modules
│   ├── discovery/        # Device discovery components
│   ├── assessment/       # Vulnerability assessment
│   └── fuzzing/          # Protocol fuzzing implementations
├── data/                 # Data files and databases
│   └── vulnerabilities.json  # Known vulnerability database
└── web/                  # Web interface components
    ├── static/           # CSS, JS, and static assets
    └── templates/        # HTML templates

examples/                 # Example usage scripts
├── basic_usage.py
└── advanced_scenarios.py

tests/                    # Test suite
├── test_framework.py
└── test_modules/

config/                   # Configuration files
├── alerting.json
├── behavioral.json
├── protection.json
└── reporting.json

docs/                     # Documentation
└── user_guide.md
```

## Configuration

JSON configuration files in the `config/` directory control framework behavior:

- `alerting.json`: Alert system and notification settings
- `behavioral.json`: Behavioral analysis parameters
- `protection.json`: Protection mechanisms settings
- `reporting.json`: Report formats and retention policies

## Architecture

Five primary components:

1. **Core Engine**: Framework coordination and plugin support
2. **Discovery Module**: Network scanning and device identification
3. **Assessment Module**: Vulnerability assessment and remediation
4. **Protection Engine**: Real-time monitoring and threat blocking
5. **Analytics Engine**: Data processing and reporting

## Development

### Prerequisites
- Python 3.8+
- Nmap network scanner
- Virtual environment recommended

### Setup

```bash
python -m venv venv
source venv/bin/activate  # Or venv\Scripts\activate on Windows
pip install -r requirements-dev.txt
pytest
```

## License

MIT License - See LICENSE file for details.
