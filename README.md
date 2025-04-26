# Aqua: Advanced IoT Security Analysis Framework

## Overview

Aqua is a sophisticated security analysis framework designed for Internet of Things (IoT) devices. It combines behavioral analysis, machine learning, and real-time monitoring to provide comprehensive security assessment and protection capabilities.

## Features

### Behavioral Analysis
- Machine learning-based anomaly detection
- Real-time network traffic analysis
- Process behavior monitoring
- File system activity tracking
- Automated pattern recognition

### Security Monitoring
- Advanced alerting system
- Multiple notification channels (Email, SIEM, Webhook)
- Configurable alert thresholds
- Common Event Format (CEF) support
- Real-time console notifications

### Analytics and Reporting
- Comprehensive statistical analysis
- Trend detection and visualization
- Customizable reporting periods
- Multiple export formats (JSON, CSV, PDF)
- Automated security recommendations

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup
1. Clone the repository:
```bash
git clone https://github.com/pandaadir05/aqua.git
cd aqua
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install the package:
```bash
pip install -e .
```

## Configuration

The framework uses JSON configuration files stored in the `config` directory:

- `alerting.json`: Alert system configuration
- `behavioral.json`: Behavioral analysis parameters
- `reporting.json`: Reporting and analytics settings

Configuration files are automatically generated with default values on first run.

## Usage

### Basic Usage
```python
from aqua.core import BehavioralAnalyzer, AlertManager, ReportGenerator

# Initialize components
analyzer = BehavioralAnalyzer()
alert_manager = AlertManager()
report_gen = ReportGenerator()

# Analyze network behavior
score = analyzer.analyze_network_behavior(network_data)

# Generate security report
report = report_gen.generate_report("daily")
```

### Advanced Configuration
```python
# Configure alert thresholds
analyzer.config["anomaly_threshold"] = 0.8

# Add processes to whitelist
analyzer.add_to_whitelist("processes", "authorized_process")

# Customize reporting metrics
report_gen.config["metrics"]["network"]["protocol_distribution"] = True
```

## Architecture

The framework consists of three main components:

1. **Behavioral Analysis Engine**
   - Anomaly detection using Isolation Forest algorithm
   - Feature extraction and scaling
   - Real-time model updates

2. **Alert Management System**
   - Multi-channel notification system
   - Configurable alert rules
   - Alert correlation and aggregation

3. **Analytics Engine**
   - Statistical analysis
   - Trend detection
   - Automated reporting

## Development

### Testing
Run the test suite:
```bash
python -m pytest tests/
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Authors

- Adir - Initial work - [Cyber Security Research]

## Acknowledgments

- Machine Learning algorithms based on scikit-learn
- Visualization powered by matplotlib
- Console interface using Rich library 