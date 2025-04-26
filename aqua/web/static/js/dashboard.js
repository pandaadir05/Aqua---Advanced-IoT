/**
 * Aqua IoT Security Platform
 * Dashboard Functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize charts and statistics
    initSecurityTrendsChart();
    initDeviceSecurityChart();
    initVulnerabilityPieChart();
    
    // Load dashboard data
    loadDashboardData();
    
    // Setup scan form handler
    setupScanForm();
    
    // Setup WebSocket connection for real-time updates
    startWebSocketConnection();
    
    // Set up refresh button
    const refreshBtn = document.getElementById('refreshDashboardBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            loadDashboardData();
        });
    }
});

/**
 * Load dashboard data
 */
function loadDashboardData() {
    // Show loading spinner
    document.querySelectorAll('.loading-spinner').forEach(spinner => {
        spinner.style.display = 'block';
    });
    
    // Make API calls to get data
    Promise.all([
        fetch('/api/devices').then(resp => resp.json()),
        fetch('/api/vulnerabilities').then(resp => resp.json()),
        fetch('/api/scans').then(resp => resp.json())
    ])
    .then(([devices, vulnerabilities, scans]) => {
        updateStatistics(devices, vulnerabilities, scans);
        updateDeviceSecurityChart(devices);
        updateVulnerabilityPieChart(vulnerabilities);
        loadCriticalVulnerabilities(vulnerabilities, devices);
        loadRecentScans(scans);
        
        // Update network visualization if available
        if (window.networkViz) {
            window.networkViz.loadData(devices);
        }
        
        // Hide loading spinners
        document.querySelectorAll('.loading-spinner').forEach(spinner => {
            spinner.style.display = 'none';
        });
    })
    .catch(error => {
        console.error('Error loading dashboard data:', error);
        
        // If API fails, load demo data
        loadDemoDashboardData();
        
        // Hide loading spinners
        document.querySelectorAll('.loading-spinner').forEach(spinner => {
            spinner.style.display = 'none';
        });
    });
}

/**
 * Load demo dashboard data if API fails
 */
function loadDemoDashboardData() {
    // Demo devices
    const devices = [
        { id: "dev_1", ip: "192.168.1.101", hostname: "iot-camera-01", device_type: "camera", manufacturer: "SecurityCam", is_online: true },
        { id: "dev_2", ip: "192.168.1.102", hostname: "smart-thermostat", device_type: "thermostat", manufacturer: "SmartHome", is_online: true },
        { id: "dev_3", ip: "192.168.1.103", hostname: "smart-lock", device_type: "lock", manufacturer: "SecureLock", is_online: true },
        { id: "dev_4", ip: "192.168.1.104", hostname: "router", device_type: "router", manufacturer: "NetLink", is_online: true },
        { id: "dev_5", ip: "192.168.1.105", hostname: "smart-tv", device_type: "tv", manufacturer: "SmartView", is_online: true }
    ];
    
    // Demo vulnerabilities
    const vulnerabilities = [
        { id: "vuln_1", name: "Default Credentials", description: "Device uses default login credentials", severity: "high", device_id: "dev_1" },
        { id: "vuln_2", name: "Unencrypted MQTT", description: "Device uses unencrypted MQTT protocol", severity: "medium", device_id: "dev_2" },
        { id: "vuln_3", name: "Outdated Firmware", description: "Device is running outdated firmware", severity: "high", device_id: "dev_3" },
        { id: "vuln_4", name: "Insecure Web Interface", description: "Device web interface has vulnerabilities", severity: "medium", device_id: "dev_1" },
        { id: "vuln_5", name: "Open Telnet Port", description: "Device has open Telnet port", severity: "critical", device_id: "dev_4" }
    ];
    
    // Demo scans
    const scans = [
        { id: "scan_1", name: "Weekly Security Scan", target: "192.168.1.0/24", status: "completed", started_at: "2023-10-15T10:00:00Z", completed_at: "2023-10-15T10:05:23Z" },
        { id: "scan_2", name: "Quick Scan", target: "192.168.1.101", status: "completed", started_at: "2023-10-14T14:30:00Z", completed_at: "2023-10-14T14:31:15Z" },
        { id: "scan_3", name: null, target: "192.168.1.0/24", status: "running", progress: 45, started_at: "2023-10-16T09:15:00Z" }
    ];
    
    // Update UI with demo data
    updateStatistics(devices, vulnerabilities, scans);
    updateDeviceSecurityChart(devices);
    updateVulnerabilityPieChart(vulnerabilities);
    loadCriticalVulnerabilities(vulnerabilities, devices);
    loadRecentScans(scans);
}

/**
 * Update dashboard statistics
 */
function updateStatistics(devices, vulnerabilities, scans) {
    // Update device count
    const deviceCount = document.getElementById('deviceCount');
    if (deviceCount) {
        deviceCount.textContent = devices.length;
    }
    
    // Update vulnerability count
    const vulnCount = document.getElementById('vulnCount');
    if (vulnCount) {
        vulnCount.textContent = vulnerabilities.length;
    }
    
    // Update critical vulnerability count
    const criticalVulnCount = document.getElementById('criticalVulnCount');
    if (criticalVulnCount) {
        const critical = vulnerabilities.filter(v => v.severity === 'critical' || v.severity === 'high').length;
        criticalVulnCount.textContent = critical;
    }
    
    // Update scan count
    const scanCount = document.getElementById('scanCount');
    if (scanCount) {
        const completedScans = scans.filter(s => s.status === 'completed').length;
        scanCount.textContent = completedScans;
    }
}

/**
 * Initialize security trends chart
 */
function initSecurityTrendsChart() {
    const chartElement = document.getElementById('securityTrendsChart');
    
    if (!chartElement) return;
    
    const options = {
        series: [
            {
                name: 'Vulnerabilities',
                type: 'column',
                data: [14, 12, 19, 21, 17, 15, 18]
            },
            {
                name: 'Threats Blocked',
                type: 'line',
                data: [34, 29, 51, 42, 33, 38, 45]
            }
        ],
        chart: {
            height: 350,
            type: 'line',
            toolbar: {
                show: false
            },
            animations: {
                enabled: true
            },
            fontFamily: 'Inter, sans-serif'
        },
        stroke: {
            curve: 'smooth',
            width: [0, 3]
        },
        colors: ['#e63757', '#2c7be5'],
        dataLabels: {
            enabled: false
        },
        xaxis: {
            categories: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        },
        yaxis: [
            {
                title: {
                    text: 'Vulnerabilities'
                }
            },
            {
                opposite: true,
                title: {
                    text: 'Threats Blocked'
                }
            }
        ],
        legend: {
            position: 'top'
        },
        fill: {
            opacity: [0.85, 1]
        },
        tooltip: {
            shared: true,
            intersect: false,
            theme: document.body.classList.contains('dark-mode') ? 'dark' : 'light'
        }
    };

    const chart = new ApexCharts(chartElement, options);
    chart.render();
}

/**
 * Initialize device security chart
 */
function initDeviceSecurityChart() {
    const chartElement = document.getElementById('deviceSecurityChart');
    
    if (!chartElement) return;
    
    const options = {
        series: [60, 30, 10],
        chart: {
            type: 'donut',
            height: 300,
            toolbar: {
                show: false
            },
            fontFamily: 'Inter, sans-serif'
        },
        labels: ['Secure', 'At Risk', 'Critical'],
        colors: ['#00b274', '#f6c343', '#e63757'],
        legend: {
            position: 'bottom'
        },
        dataLabels: {
            enabled: false
        },
        tooltip: {
            enabled: true,
            theme: document.body.classList.contains('dark-mode') ? 'dark' : 'light'
        },
        responsive: [{
            breakpoint: 480,
            options: {
                chart: {
                    height: 250
                },
                legend: {
                    position: 'bottom'
                }
            }
        }]
    };

    window.deviceSecurityChart = new ApexCharts(chartElement, options);
    window.deviceSecurityChart.render();
}

/**
 * Update device security chart
 */
function updateDeviceSecurityChart(devices) {
    if (!window.deviceSecurityChart || !devices.length) return;
    
    // Count devices by security status
    const secure = devices.filter(d => !d.vulnerabilities || d.vulnerabilities.length === 0).length;
    const atRisk = devices.filter(d => 
        d.vulnerabilities && 
        d.vulnerabilities.length > 0 && 
        !d.vulnerabilities.some(v => v.severity === 'critical' || v.severity === 'high')
    ).length;
    const critical = devices.filter(d => 
        d.vulnerabilities && 
        d.vulnerabilities.some(v => v.severity === 'critical' || v.severity === 'high')
    ).length;
    
    // Update chart
    window.deviceSecurityChart.updateSeries([secure, atRisk, critical]);
}

/**
 * Initialize vulnerability pie chart
 */
function initVulnerabilityPieChart() {
    const chartElement = document.getElementById('vulnerabilityPieChart');
    
    if (!chartElement) return;
    
    const options = {
        series: [40, 30, 20, 10],
        chart: {
            type: 'pie',
            height: 300,
            toolbar: {
                show: false
            },
            fontFamily: 'Inter, sans-serif'
        },
        labels: ['High', 'Medium', 'Low', 'Info'],
        colors: ['#e63757', '#f6c343', '#00b274', '#2c7be5'],
        legend: {
            position: 'bottom'
        },
        dataLabels: {
            enabled: false
        },
        tooltip: {
            enabled: true,
            theme: document.body.classList.contains('dark-mode') ? 'dark' : 'light'
        },
        responsive: [{
            breakpoint: 480,
            options: {
                chart: {
                    height: 250
                },
                legend: {
                    position: 'bottom'
                }
            }
        }]
    };

    window.vulnerabilityPieChart = new ApexCharts(chartElement, options);
    window.vulnerabilityPieChart.render();
}

/**
 * Update vulnerability distribution pie chart
 */
function updateVulnerabilityPieChart(vulnerabilities) {
    if (!window.vulnerabilityPieChart || !vulnerabilities.length) return;
    
    // Count vulnerabilities by severity
    const critical = vulnerabilities.filter(v => v.severity === 'critical').length;
    const high = vulnerabilities.filter(v => v.severity === 'high').length;
    const medium = vulnerabilities.filter(v => v.severity === 'medium').length;
    const low = vulnerabilities.filter(v => v.severity === 'low').length;
    const info = vulnerabilities.filter(v => v.severity === 'info').length;
    
    // Combine critical and high for simplicity
    const highTotal = critical + high;
    
    // Update chart
    window.vulnerabilityPieChart.updateSeries([highTotal, medium, low, info]);
}

/**
 * Load critical vulnerabilities table
 */
function loadCriticalVulnerabilities(vulnerabilities, devices) {
    const tableBody = document.getElementById('criticalVulnerabilitiesTable');
    if (!tableBody) return;
    
    // Clear existing content
    tableBody.innerHTML = '';
    
    // Sort and filter vulnerabilities
    const criticalVulns = vulnerabilities
        .filter(v => v.severity === 'critical' || v.severity === 'high')
        .sort((a, b) => a.severity === 'critical' ? -1 : 1);
    
    // Take top 5
    const topVulns = criticalVulns.slice(0, 5);
    
    if (topVulns.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="4" class="text-center">No critical vulnerabilities found</td></tr>';
        return;
    }
    
    // Add vulnerabilities to table
    topVulns.forEach(vuln => {
        const device = devices.find(d => d.id === vuln.device_id) || { ip: 'Unknown', hostname: 'Unknown' };
        
        const row = document.createElement('tr');
        
        const severityClass = vuln.severity === 'critical' ? 'danger' : 'warning';
        
        row.innerHTML = `
            <td>
                <strong>${vuln.name}</strong><br>
                <small class="text-muted">${device.hostname || device.ip}</small>
            </td>
            <td>${vuln.description}</td>
            <td><span class="badge bg-${severityClass}">${vuln.severity}</span></td>
            <td>
                <button class="btn btn-sm btn-outline-primary">View</button>
                <button class="btn btn-sm btn-outline-success">Fix</button>
            </td>
        `;
        
        tableBody.appendChild(row);
    });
}

/**
 * Load recent scans table
 */
function loadRecentScans(scans) {
    const tableBody = document.getElementById('recentScansTable');
    if (!tableBody) return;
    
    // Clear existing content
    tableBody.innerHTML = '';
    
    // Sort scans by date (most recent first)
    const sortedScans = [...scans].sort((a, b) => 
        new Date(b.started_at) - new Date(a.started_at)
    );
    
    // Take most recent 5
    const recentScans = sortedScans.slice(0, 5);
    
    if (recentScans.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="4" class="text-center">No recent scans found</td></tr>';
        return;
    }
    
    // Add scans to table
    recentScans.forEach(scan => {
        const row = document.createElement('tr');
        
        // Format the date/time
        const startDate = new Date(scan.started_at);
        const formattedDate = startDate.toLocaleString();
        
        // Determine status class
        let statusClass = '';
        switch(scan.status) {
            case 'completed':
                statusClass = 'success';
                break;
            case 'running':
                statusClass = 'primary';
                break;
            case 'failed':
                statusClass = 'danger';
                break;
            case 'stopped':
                statusClass = 'warning';
                break;
            default:
                statusClass = 'secondary';
        }
        
        row.innerHTML = `
            <td>${scan.name || `Scan of ${scan.target}`}</td>
            <td>${scan.target}</td>
            <td>${formattedDate}</td>
            <td>
                <span class="badge bg-${statusClass}">
                    ${scan.status === 'running' ? `${scan.progress || 0}%` : scan.status}
                </span>
            </td>
        `;
        
        tableBody.appendChild(row);
    });
}

/**
 * Update active step in the scan progress
 * @param {number} step - The active step (1-based)
 */
function updateActiveStep(step) {
    const scanSteps = document.querySelectorAll('.scan-step');
    
    scanSteps.forEach((stepEl, index) => {
        if (index < step) {
            stepEl.classList.add('active');
        } else {
            stepEl.classList.remove('active');
        }
    });
}

/**
 * Update scan status in UI
 */
function updateScanStatus(scanId, status, progress) {
    const scanProgressBar = document.getElementById('scanProgressBar');
    const scanProgressText = document.getElementById('scanProgressText');
    const scanProgressStatus = document.getElementById('scanProgressStatus');
    const scanProgressCircle = document.querySelector('.progress-ring-circle');
    const progressTextElement = document.querySelector('.scan-progress-circle .progress-text');
    const scanLogContainer = document.getElementById('scanLogContainer');
    
    // Update progress bar if it exists
    if (scanProgressBar) scanProgressBar.style.width = `${progress}%`;
    
    // Update status text if it exists
    if (scanProgressStatus) scanProgressStatus.textContent = status;
    
    // Update progress circle animation if it exists
    if (scanProgressCircle) {
        const radius = scanProgressCircle.r.baseVal.value;
        const circumference = 2 * Math.PI * radius;
        const offset = circumference - (progress / 100) * circumference;
        
        scanProgressCircle.style.strokeDasharray = `${circumference} ${circumference}`;
        scanProgressCircle.style.strokeDashoffset = offset;
        
        // Update color based on progress
        if (progress < 30) {
            scanProgressCircle.style.stroke = '#2c7be5'; // Blue for early stages
        } else if (progress < 60) {
            scanProgressCircle.style.stroke = '#00b274'; // Green for mid stages
        } else if (progress < 90) {
            scanProgressCircle.style.stroke = '#f6c343'; // Yellow for later stages
        } else {
            scanProgressCircle.style.stroke = '#e63757'; // Red for final stages
        }
    }
    
    // Update progress text inside circle
    if (progressTextElement) {
        progressTextElement.textContent = `${progress}%`;
        
        // Add animation pulse effect on certain thresholds
        if (progress % 25 === 0) {
            progressTextElement.classList.add('pulse-animation');
            setTimeout(() => {
                progressTextElement.classList.remove('pulse-animation');
            }, 1000);
        }
    }
    
    // Update log based on progress
    if (scanLogContainer) {
        // Add log entry based on progress
        if (progress <= 10 && !scanLogContainer.querySelector('.log-entry[data-phase="init"]')) {
            addLogEntry(scanLogContainer, '[INFO] Initializing scan...', 'init');
        } else if (progress > 10 && progress <= 30 && !scanLogContainer.querySelector('.log-entry[data-phase="discovery"]')) {
            addLogEntry(scanLogContainer, '[INFO] Performing host discovery...', 'discovery');
        } else if (progress > 30 && progress <= 60 && !scanLogContainer.querySelector('.log-entry[data-phase="ports"]')) {
            addLogEntry(scanLogContainer, '[INFO] Scanning ports and services...', 'ports');
        } else if (progress > 60 && progress <= 80 && !scanLogContainer.querySelector('.log-entry[data-phase="vulns"]')) {
            addLogEntry(scanLogContainer, '[INFO] Analyzing vulnerabilities...', 'vulns');
        } else if (progress > 80 && progress < 100 && !scanLogContainer.querySelector('.log-entry[data-phase="results"]')) {
            addLogEntry(scanLogContainer, '[INFO] Processing results...', 'results');
        } else if (progress >= 100 && status === 'completed' && !scanLogContainer.querySelector('.log-entry[data-phase="complete"]')) {
            addLogEntry(scanLogContainer, '[INFO] Scan completed successfully', 'complete');
            
            // Close the modal after a delay
            setTimeout(() => {
                const progressModal = bootstrap.Modal.getInstance(document.getElementById('scanProgressModal'));
                if (progressModal) progressModal.hide();
                
                // Refresh dashboard data
                loadDashboardData();
            }, 2000);
        }
    }
    
    // Update the scan steps based on progress
    if (progress <= 20) {
        updateActiveStep(1);
    } else if (progress <= 40) {
        updateActiveStep(2);
    } else if (progress <= 60) {
        updateActiveStep(3); 
    } else if (progress <= 80) {
        updateActiveStep(4);
    } else if (progress >= 100) {
        updateActiveStep(5);
    }
    
    if (scanProgressText) {
        if (progress <= 25) {
            scanProgressText.innerHTML = `<span class="badge bg-info me-2">Discovery</span> <span class="text-muted">${progress}% complete</span>`;
        } else if (progress <= 50) {
            scanProgressText.innerHTML = `<span class="badge bg-primary me-2">Ports</span> <span class="text-muted">${progress}% complete</span>`;
        } else if (progress <= 75) {
            scanProgressText.innerHTML = `<span class="badge bg-warning me-2">Vulnerabilities</span> <span class="text-muted">${progress}% complete</span>`;
        } else {
            scanProgressText.innerHTML = `<span class="badge bg-danger me-2">Analysis</span> <span class="text-muted">${progress}% complete</span>`;
        }
        
        if (progress >= 100) {
            scanProgressText.innerHTML = '<span class="badge bg-success me-2">Completed</span> <span class="text-success">100% complete</span>';
        } else if (status === 'failed') {
            scanProgressText.innerHTML = '<span class="badge bg-danger me-2">Failed</span> Scan failed!';
        } else if (status === 'stopped') {
            scanProgressText.innerHTML = '<span class="badge bg-warning me-2">Stopped</span> Scan stopped.';
        }
    }
}

/**
 * Add a log entry to the scan log
 */
function addLogEntry(container, message, phase) {
    const entry = document.createElement('div');
    entry.className = 'log-entry';
    entry.setAttribute('data-phase', phase);
    entry.textContent = message;
    
    // Add timestamp
    const timestamp = new Date().toLocaleTimeString();
    entry.textContent = `[${timestamp}] ${message}`;
    
    container.appendChild(entry);
    
    // Auto-scroll to bottom
    container.scrollTop = container.scrollHeight;
    
    // Add subtle animation
    entry.style.opacity = '0';
    entry.style.transform = 'translateX(-10px)';
    setTimeout(() => {
        entry.style.opacity = '1';
        entry.style.transform = 'translateX(0)';
    }, 10);
}

/**
 * Setup cancel scan button
 */
function setupCancelScanButton() {
    const cancelScanBtn = document.getElementById('cancelScanBtn');
    if (!cancelScanBtn) return;
    
    cancelScanBtn.addEventListener('click', function() {
        const scanId = this.getAttribute('data-scan-id');
        if (!scanId) {
            console.error('No scan ID found for cancellation');
            return;
        }
        
        this.disabled = true;
        this.innerHTML = '<i class="bi bi-hourglass-split me-1"></i>Cancelling...';
        
        // Send cancel request to API
        fetch(`/api/scans/${scanId}/stop`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(result => {
            console.log('Scan cancelled:', result);
            const scanProgressText = document.getElementById('scanProgressText');
            if (scanProgressText) {
                scanProgressText.innerHTML = '<span class="badge bg-warning me-2">Cancelled</span> Scan cancelled by user';
            }
            
            const scanLogContainer = document.getElementById('scanLogContainer');
            if (scanLogContainer) {
                addLogEntry(scanLogContainer, '[WARNING] Scan cancelled by user', 'cancelled');
            }
            
            // Close modal after a short delay
            setTimeout(() => {
                const modal = bootstrap.Modal.getInstance(document.getElementById('scanProgressModal'));
                if (modal) modal.hide();
            }, 2000);
        })
        .catch(error => {
            console.error('Error cancelling scan:', error);
            this.disabled = false;
            this.innerHTML = '<i class="bi bi-stop-fill me-1"></i>Cancel Scan';
        });
    });
}

/**
 * Set up scan form
 */
function setupScanForm() {
    const startScanBtn = document.getElementById('startScanBtn');
    
    if (startScanBtn) {
        startScanBtn.addEventListener('click', function() {
            // Get form data
            const scanTarget = document.getElementById('scanTarget').value;
            const scanName = document.getElementById('scanName').value;
            const scanType = document.getElementById('scanType').value;
            
            if (!scanTarget) {
                alert('Please enter a target IP or network range');
                return;
            }
            
            // Close the modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('newScanModal'));
            modal.hide();
            
            // Show progress modal
            const progressModal = new bootstrap.Modal(document.getElementById('scanProgressModal'));
            progressModal.show();
            
            // Reset progress bar
            const scanProgressBar = document.getElementById('scanProgressBar');
            const scanProgressText = document.getElementById('scanProgressText');
            const scanProgressTarget = document.getElementById('scanProgressTarget');
            const scanProgressType = document.getElementById('scanProgressType');
            const scanLogContainer = document.getElementById('scanLogContainer');
            
            if (scanProgressBar) scanProgressBar.style.width = '0%';
            if (scanProgressText) scanProgressText.textContent = 'Starting scan...';
            if (scanProgressTarget) scanProgressTarget.textContent = scanTarget;
            if (scanProgressType) scanProgressType.textContent = scanType;
            if (scanLogContainer) scanLogContainer.innerHTML = '<div class="log-entry">[INFO] Initializing scan...</div>';
            
            // Set current time
            const scanProgressTime = document.getElementById('scanProgressTime');
            if (scanProgressTime) {
                scanProgressTime.textContent = new Date().toLocaleString();
            }
            
            // Create scan data
            const data = {
                target: scanTarget,
                scan_type: scanType
            };
            
            if (scanName) {
                data.name = scanName;
            }
            
            console.log('Starting scan with data:', data);
            
            // Start the scan via API
            fetch('/api/scans', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(result => {
                console.log('Scan started:', result);
                if (result.scan_id) {
                    // Store scan ID for cancellation
                    const cancelScanBtn = document.getElementById('cancelScanBtn');
                    if (cancelScanBtn) {
                        cancelScanBtn.setAttribute('data-scan-id', result.scan_id);
                    }
                    
                    // Add a log entry
                    if (scanLogContainer) {
                        addLogEntry(scanLogContainer, `[INFO] Scan started with ID: ${result.scan_id}`, 'start');
                    }
                    
                    // The progress will be updated via WebSocket
                    trackScanProgress(result.scan_id);
                } else {
                    throw new Error('No scan ID returned');
                }
            })
            .catch(error => {
                console.error('Error starting scan:', error);
                
                // Show error in log
                if (scanLogContainer) {
                    addLogEntry(scanLogContainer, `[ERROR] Failed to start scan: ${error.message}`, 'error');
                }
                
                // Update progress text with error
                if (scanProgressText) {
                    scanProgressText.textContent = 'Scan failed to start';
                }
                
                // Don't close the modal, let the user see the error
                // Instead, add a close button
                const footerDiv = document.createElement('div');
                footerDiv.className = 'text-center mt-3';
                footerDiv.innerHTML = `
                    <button type="button" class="btn btn-secondary" onclick="bootstrap.Modal.getInstance(document.getElementById('scanProgressModal')).hide()">
                        Close
                    </button>
                `;
                
                if (scanLogContainer) {
                    scanLogContainer.appendChild(footerDiv);
                }
            });
        });
    }
    
    // Setup cancel button
    setupCancelScanButton();
}

/**
 * Track scan progress and update UI
 */
function trackScanProgress(scanId) {
    console.log('Tracking scan progress for ID:', scanId);
    // This function will be called after a scan is started
    // The progress updates will come from WebSocket
    
    // Poll for scan status in case WebSocket fails
    const statusInterval = setInterval(() => {
        console.log('Polling scan status for ID:', scanId);
        fetch(`/api/scans/${scanId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(scan => {
                console.log('Scan status received:', scan);
                updateScanStatus(scanId, scan.status, scan.progress);
                
                if (scan.status !== 'running') {
                    clearInterval(statusInterval);
                    
                    // If scan completed, refresh dashboard data
                    if (scan.status === 'completed') {
                        loadDashboardData();
                    }
                }
            })
            .catch(error => {
                console.error('Error checking scan status:', error);
                clearInterval(statusInterval);
            });
    }, 3000);
}

/**
 * Set up WebSocket connection for real-time updates
 */
function startWebSocketConnection() {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${wsProtocol}//${window.location.host}/ws`;
    
    try {
        const socket = new WebSocket(wsUrl);
        
        socket.onopen = function(e) {
            console.log('WebSocket connection established');
        };
        
        socket.onmessage = function(event) {
            console.log('WebSocket message received:', event.data);
            try {
                const data = JSON.parse(event.data);
                
                // Handle different message types
                switch(data.type) {
                    case 'scan_progress':
                        updateScanStatus(data.scan_id, 'running', data.progress);
                        break;
                        
                    case 'scan_completed':
                        // Refresh data when scan completes
                        loadDashboardData();
                        break;
                        
                    case 'scan_error':
                        console.error('Scan error:', data.error);
                        updateScanStatus(data.scan_id, 'failed', 100);
                        break;
                        
                    case 'new_alert':
                        addNotification(data.alert);
                        break;
                        
                    case 'device_update':
                        // Refresh data when device is updated
                        loadDashboardData();
                        break;
                }
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        };
        
        socket.onclose = function(event) {
            console.log('WebSocket connection closed', event);
            if (!event.wasClean) {
                console.log('WebSocket connection closed unexpectedly. Reconnecting...');
                // Try to reconnect after a delay
                setTimeout(startWebSocketConnection, 3000);
            }
        };
        
        socket.onerror = function(error) {
            console.error('WebSocket error:', error);
        };
        
        // Keep connection alive
        setInterval(() => {
            if (socket && socket.readyState === WebSocket.OPEN) {
                socket.send(JSON.stringify({type: 'ping'}));
            }
        }, 30000);
        
        // Store socket in window for global access
        window.scannerWebSocket = socket;
    } catch (error) {
        console.error('Error setting up WebSocket:', error);
    }
}
