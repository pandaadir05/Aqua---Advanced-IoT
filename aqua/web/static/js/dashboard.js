document.addEventListener('DOMContentLoaded', function() {
    // Update stats
    fetchStats();
    
    // Set up scan form submission
    setupScanForm();
    
    // Refresh data every 30 seconds
    setInterval(fetchStats, 30000);
});

function fetchStats() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            document.getElementById('total-scans').textContent = data.total_scans || 0;
            document.getElementById('total-devices').textContent = data.total_devices || 0;
            document.getElementById('total-vulnerabilities').textContent = data.total_vulnerabilities || 0;
        })
        .catch(error => console.error('Error fetching stats:', error));
}

function setupScanForm() {
    const form = document.getElementById('scan-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(form);
            const data = {};
            for (let [key, value] of formData.entries()) {
                data[key] = value;
            }
            
            fetch('/api/scan', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                // Close the modal
                const scanModal = bootstrap.Modal.getInstance(document.getElementById('newScanModal'));
                scanModal.hide();
                
                // Show progress modal
                document.getElementById('scanProgressTarget').textContent = data.target;
                document.getElementById('scanProgressType').textContent = data.scan_type;
                const progressModal = new bootstrap.Modal(document.getElementById('scanProgressModal'));
                progressModal.show();
                
                // Start tracking scan progress
                trackScanProgress(result.scan_id);
                
                // Add entry to recent scans table
                addRecentScan({
                    id: result.scan_id,
                    name: data.name || `Scan of ${data.target}`,
                    target: data.target,
                    status: 'running',
                    progress: 0
                });
            })
            .catch(error => {
                console.error('Error starting scan:', error);
                alert('Error starting scan. Please try again.');
            });
        });
    }
}

/**
 * Track scan progress and update UI
 */
function trackScanProgress(scanId) {
    const progressCircle = document.querySelector('.progress-ring-circle');
    const progressText = document.querySelector('.progress-text');
    const logContainer = document.getElementById('scanLogContainer');
    
    // Calculate circumference
    const radius = parseFloat(progressCircle.getAttribute('r'));
    const circumference = 2 * Math.PI * radius;
    progressCircle.style.strokeDasharray = circumference;
    
    function updateProgress(progress) {
        const offset = circumference - (progress / 100) * circumference;
        progressCircle.style.strokeDashoffset = offset;
        progressText.textContent = `${progress}%`;
        
        // Add log entry
        const logEntry = document.createElement('div');
        logEntry.classList.add('log-entry');
        logEntry.textContent = `[INFO] Scanning progress: ${progress}%`;
        logContainer.appendChild(logEntry);
        logContainer.scrollTop = logContainer.scrollHeight;
    }
    
    // Initial check
    checkScanStatus();
    
    // Set up interval to check status
    const statusInterval = setInterval(checkScanStatus, 2000);
    
    function checkScanStatus() {
        fetch(`/api/scan/${scanId}`)
            .then(response => response.json())
            .then(data => {
                updateProgress(data.progress);
                
                // Update status
                document.getElementById('scanProgressStatus').textContent = data.status.charAt(0).toUpperCase() + data.status.slice(1);
                
                // If scan is complete or failed, clear interval
                if (data.status === 'completed' || data.status === 'failed') {
                    clearInterval(statusInterval);
                    
                    // Add completion log
                    const logEntry = document.createElement('div');
                    logEntry.classList.add('log-entry');
                    logEntry.textContent = `[INFO] Scan ${data.status}`;
                    logContainer.appendChild(logEntry);
                    
                    // Update recent scans table
                    updateScanStatus(scanId, data.status, data.progress);
                    
                    // Refresh dashboard data
                    loadDashboardData();
                }
            })
            .catch(error => {
                console.error('Error checking scan status:', error);
                clearInterval(statusInterval);
            });
    }
}

/**
 * Add scan to recent scans table
 */
function addRecentScan(scan) {
    const recentScansTable = document.getElementById('recentScansTable');
    
    if (recentScansTable) {
        const row = document.createElement('tr');
        row.setAttribute('data-scan-id', scan.id);
        
        row.innerHTML = `
            <td>${scan.name || 'Unnamed scan'}</td>
            <td>${scan.target}</td>
            <td>
                <span class="status-${scan.status}">${scan.status.charAt(0).toUpperCase() + scan.status.slice(1)}</span>
            </td>
            <td>
                <div class="progress" style="height: 5px;">
                    <div class="progress-bar" role="progressbar" style="width: ${scan.progress}%" aria-valuenow="${scan.progress}" aria-valuemin="0" aria-valuemax="100"></div>
                </div>
                <small class="progress-text">${scan.progress}%</small>
            </td>
        `;
        
        // Insert at the beginning
        if (recentScansTable.querySelector('tbody tr')) {
            recentScansTable.querySelector('tbody').insertBefore(row, recentScansTable.querySelector('tbody tr'));
        } else {
            recentScansTable.querySelector('tbody').appendChild(row);
        }
    }
}

/**
 * Update scan status in the recent scans table
 */
function updateScanStatus(scanId, status, progress) {
    const recentScansTable = document.getElementById('recentScansTable');
    
    if (recentScansTable) {
        const row = recentScansTable.querySelector(`tr[data-scan-id="${scanId}"]`);
        
        if (row) {
            const statusCell = row.querySelector('td:nth-child(3)');
            const progressCell = row.querySelector('td:nth-child(4)');
            
            statusCell.innerHTML = `<span class="status-${status}">${status.charAt(0).toUpperCase() + status.slice(1)}</span>`;
            progressCell.querySelector('.progress-bar').style.width = `${progress}%`;
            progressCell.querySelector('.progress-text').textContent = `${progress}%`;
        }
    }
}

/**
 * Load dashboard data and update UI
 */
function loadDashboardData() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            updateStatCards(data);
            updateRiskGauge(data.risk_score);
            updateRiskFactors(data.risk_factors);
            updateTrendsChart(data.trends);
            updateVulnerabilityPieChart(data.vulnerability_severity);
            loadDevicesTable();
            loadVulnerabilitiesTable();
            loadScansTable();
        })
        .catch(error => {
            console.error('Error loading dashboard data:', error);
        });
}

/**
 * Update stat cards with latest numbers
 */
function updateStatCards(data) {
    document.getElementById('deviceCount').textContent = data.total_devices;
    document.getElementById('vulnCount').textContent = data.total_vulnerabilities;
    document.getElementById('riskScore').textContent = data.risk_score;
    document.getElementById('scanCount').textContent = data.completed_scans;
}

/**
 * Update risk gauge chart
 */
function updateRiskGauge(score) {
    const gaugeElement = document.getElementById('riskGaugeChart');
    
    if (!gaugeElement) return;
    
    // Clear previous chart if it exists
    gaugeElement.innerHTML = '';
    
    const options = {
        series: [score],
        chart: {
            type: 'radialBar',
            height: 250,
            toolbar: {
                show: false
            }
        },
        plotOptions: {
            radialBar: {
                startAngle: -135,
                endAngle: 135,
                hollow: {
                    margin: 0,
                    size: '70%'
                },
                track: {
                    background: '#e7e7e7',
                    strokeWidth: '97%',
                    margin: 5,
                    dropShadow: {
                        enabled: false,
                    }
                },
                dataLabels: {
                    name: {
                        show: true,
                        fontSize: '16px',
                        fontFamily: 'Segoe UI, sans-serif',
                        fontWeight: 600,
                        color: undefined,
                        offsetY: -10
                    },
                    value: {
                        offsetY: 0,
                        fontSize: '22px',
                        fontFamily: 'Segoe UI, sans-serif',
                        fontWeight: 700,
                        color: undefined,
                        formatter: function (val) {
                            return val;
                        }
                    }
                }
            }
        },
        fill: {
            type: 'gradient',
            gradient: {
                shade: 'dark',
                shadeIntensity: 0.15,
                inverseColors: false,
                opacityFrom: 1,
                opacityTo: 1,
                stops: [0, 50, 100],
                colorStops: [
                    {
                        offset: 0,
                        color: '#00b274',
                        opacity: 1
                    },
                    {
                        offset: 50,
                        color: '#f6c343',
                        opacity: 1
                    },
                    {
                        offset: 100,
                        color: '#e63757',
                        opacity: 1
                    }
                ]
            }
        },
        stroke: {
            dashArray: 4
        },
        labels: ['Risk Score'],
    };

    const chart = new ApexCharts(gaugeElement, options);
    chart.render();
}

/**
 * Update risk factors list
 */
function updateRiskFactors(factors) {
    const container = document.getElementById('riskFactorsList');
    
    if (!container) return;
    
    container.innerHTML = '';
    
    factors.forEach(factor => {
        const item = document.createElement('div');
        item.classList.add('risk-factor-item');
        
        let colorClass = 'bg-green';
        if (factor.impact > 20) colorClass = 'bg-yellow';
        if (factor.impact > 25) colorClass = 'bg-red';
        
        item.innerHTML = `
            <div class="w-100">
                <div class="d-flex justify-content-between">
                    <span class="risk-factor-name">${factor.factor}</span>
                    <span class="risk-factor-value">${factor.impact}%</span>
                </div>
                <div class="risk-factor-bar">
                    <div class="risk-factor-progress ${colorClass}" style="width: ${factor.impact}%"></div>
                </div>
            </div>
        `;
        
        container.appendChild(item);
    });
}

/**
 * Update trends chart
 */
function updateTrendsChart(trendsData) {
    const chartElement = document.getElementById('trendsChart');
    
    if (!chartElement) return;
    
    // Clear previous chart if it exists
    chartElement.innerHTML = '';
    
    const options = {
        series: [
            {
                name: 'Vulnerabilities',
                data: trendsData.vulnerabilities
            },
            {
                name: 'Devices',
                data: trendsData.devices
            }
        ],
        chart: {
            type: 'line',
            height: 300,
            toolbar: {
                show: false
            },
            zoom: {
                enabled: false
            }
        },
        colors: ['#e63757', '#2c7be5'],
        dataLabels: {
            enabled: false
        },
        stroke: {
            curve: 'smooth',
            width: 3
        },
        grid: {
            borderColor: '#e0e0e0',
            strokeDashArray: 4,
            xaxis: {
                lines: {
                    show: true
                }
            }
        },
        markers: {
            size: 4,
            colors: ['#e63757', '#2c7be5'],
            strokeColors: '#fff',
            strokeWidth: 2
        },
        xaxis: {
            categories: trendsData.dates,
            labels: {
                style: {
                    colors: '#95aac9',
                    fontSize: '12px',
                    fontFamily: 'Segoe UI, sans-serif',
                }
            }
        },
        yaxis: {
            labels: {
                style: {
                    colors: '#95aac9',
                    fontSize: '12px',
                    fontFamily: 'Segoe UI, sans-serif',
                }
            }
        },
        legend: {
            position: 'top',
            horizontalAlign: 'right',
            offsetY: -15,
            fontFamily: 'Segoe UI, sans-serif',
            fontSize: '13px',
        },
        tooltip: {
            theme: 'light',
            y: {
                formatter: function(value) {
                    return value;
                }
            }
        }
    };

    const chart = new ApexCharts(chartElement, options);
    chart.render();
    
    // Add event listeners for chart filters
    const filters = document.querySelectorAll('[data-chart-filter]');
    filters.forEach(filter => {
        filter.addEventListener('click', function() {
            const filterType = this.getAttribute('data-chart-filter');
            
            // Update active class
            filters.forEach(f => f.classList.remove('active'));
            this.classList.add('active');
            
            // Update chart based on filter
            if (filterType === 'vulnerabilities') {
                chart.updateSeries([
                    {
                        name: 'Vulnerabilities',
                        data: trendsData.vulnerabilities
                    }
                ]);
            } else if (filterType === 'devices') {
                chart.updateSeries([
                    {
                        name: 'Devices',
                        data: trendsData.devices
                    }
                ]);
            }
        });
    });
}

/**
 * Update vulnerability distribution pie chart
 */
function updateVulnerabilityPieChart(severityData) {
    const chartElement = document.getElementById('vulnerabilityPieChart');
    const legendElement = document.getElementById('vulnPieLegend');
    
    if (!chartElement) return;
    
    // Clear previous chart if it exists
    chartElement.innerHTML = '';
    
    const severities = Object.keys(severityData);
    const counts = Object.values(severityData);
    
    const options = {
        series: counts,
        chart: {
            type: 'donut',
            height: 240
        },
        labels: severities,
        colors: ['#e63757', '#fd7e14', '#f6c343', '#39afd1'],
        plotOptions: {
            pie: {
                donut: {
                    size: '65%'
                }
            }
        },
        dataLabels: {
            enabled: false
        },
        legend: {
            show: false
        },
        tooltip: {
            y: {
                formatter: function(value) {
                    return value + ' vulnerabilities';
                }
            }
        }
    };

    const chart = new ApexCharts(chartElement, options);
    chart.render();
    
    // Create custom legend
    if (legendElement) {
        legendElement.innerHTML = '';
        
        const colors = ['#e63757', '#fd7e14', '#f6c343', '#39afd1'];
        
        severities.forEach((severity, index) => {
            const legendItem = document.createElement('div');
            legendItem.classList.add('d-flex', 'align-items-center', 'mb-2');
            
            legendItem.innerHTML = `
                <div style="width: 12px; height: 12px; background-color: ${colors[index]}; margin-right: 8px; border-radius: 2px;"></div>
                <div class="me-auto">${severity}</div>
                <div class="fw-bold">${counts[index]}</div>
            `;
            
            legendElement.appendChild(legendItem);
        });
    }
}

/**
 * Load and populate devices table
 */
function loadDevicesTable() {
    const tableElement = document.getElementById('vulnerableDevicesTable');
    
    if (!tableElement) return;
    
    fetch('/api/devices')
        .then(response => response.json())
        .then(devices => {
            // Sort devices by risk score descending
            devices.sort((a, b) => b.risk_score - a.risk_score);
            
            // Take top 5
            const topDevices = devices.slice(0, 5);
            
            // Clear and populate table
            tableElement.innerHTML = '';
            
            topDevices.forEach(device => {
                const row = document.createElement('tr');
                
                // Determine icon based on device type
                let iconClass = 'bi-hdd';
                if (device.type.toLowerCase().includes('camera')) iconClass = 'bi-camera-video';
                if (device.type.toLowerCase().includes('router')) iconClass = 'bi-router';
                if (device.type.toLowerCase().includes('speaker')) iconClass = 'bi-speaker';
                if (device.type.toLowerCase().includes('lock')) iconClass = 'bi-lock';
                if (device.type.toLowerCase().includes('thermostat')) iconClass = 'bi-thermometer';
                
                // Determine color based on risk score
                let colorClass = 'bg-green';
                if (device.risk_score > 40) colorClass = 'bg-yellow';
                if (device.risk_score > 70) colorClass = 'bg-red';
                
                row.innerHTML = `
                    <td>
                        <div class="device-name">
                            <div class="device-icon ${colorClass}">
                                <i class="bi ${iconClass}"></i>
                            </div>
                            <div>
                                <div class="fw-medium">${device.ip}</div>
                                <div class="small text-muted">${device.manufacturer}</div>
                            </div>
                        </div>
                    </td>
                    <td>${device.type}</td>
                    <td>
                        <div class="d-flex align-items-center">
                            <span class="fw-medium me-2">${device.risk_score}</span>
                            <div class="progress flex-grow-1" style="height: 5px;">
                                <div class="progress-bar ${colorClass}" role="progressbar" style="width: ${device.risk_score}%"></div>
                            </div>
                        </div>
                    </td>
                    <td>
                        <span class="badge bg-danger">${device.vulnerabilities}</span>
                    </td>
                    <td>
                        <div class="dropdown">
                            <button class="btn btn-sm btn-outline-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown">
                                Actions
                            </button>
                            <ul class="dropdown-menu">
                                <li><a class="dropdown-item" href="/devices?id=${device.id}">View Details</a></li>
                                <li><a class="dropdown-item" href="#">Run Scan</a></li>
                                <li><hr class="dropdown-divider"></li>
                                <li><a class="dropdown-item text-danger" href="#">Block Device</a></li>
                            </ul>
                        </div>
                    </td>
                `;
                
                tableElement.appendChild(row);
            });
        })
        .catch(error => {
            console.error('Error loading devices:', error);
        });
}

/**
 * Load and populate vulnerabilities table
 */
function loadVulnerabilitiesTable() {
    const tableElement = document.getElementById('criticalVulnerabilitiesTable');
    
    if (!tableElement) return;
    
    fetch('/api/vulnerabilities')
        .then(response => response.json())
        .then(vulnerabilities => {
            // Filter for critical vulnerabilities
            const criticalVulnerabilities = vulnerabilities.filter(v => 
                v.severity === 'Critical' || v.severity === 'High'
            ).slice(0, 5);
            
            // Clear and populate table
            tableElement.innerHTML = '';
            
            criticalVulnerabilities.forEach(vuln => {
                const row = document.createElement('tr');
                
                // Get device info
                fetch(`/api/devices/${vuln.device_id}`)
                    .then(response => response.json())
                    .then(device => {
                        const severityClass = vuln.severity === 'Critical' ? 'badge-critical' : 'badge-high';
                        
                        row.innerHTML = `
                            <td>
                                <div class="fw-medium">${vuln.name}</div>
                                <div class="small text-muted">${vuln.details}</div>
                            </td>
                            <td>
                                <div class="fw-medium">${device.ip}</div>
                                <div class="small text-muted">${device.type}</div>
                            </td>
                            <td>
                                <span class="badge ${severityClass}">${vuln.severity}</span>
                            </td>
                            <td>
                                <div class="dropdown">
                                    <button class="btn btn-sm btn-outline-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown">
                                        Actions
                                    </button>
                                    <ul class="dropdown-menu">
                                        <li><a class="dropdown-item" href="/vulnerabilities?id=${vuln.id}">View Details</a></li>
                                        <li><a class="dropdown-item" href="#">Remediation Guide</a></li>
                                        <li><hr class="dropdown-divider"></li>
                                        <li><a class="dropdown-item text-danger" href="#">Mark as Fixed</a></li>
                                    </ul>
                                </div>
                            </td>
                        `;
                        
                        tableElement.appendChild(row);
                    })
                    .catch(error => {
                        console.error('Error loading device info:', error);
                    });
            });
        })
        .catch(error => {
            console.error('Error loading vulnerabilities:', error);
        });
}

/**
 * Load and populate recent scans table
 */
function loadScansTable() {
    const tableElement = document.getElementById('recentScansTable');
    
    if (!tableElement) return;
    
    fetch('/api/scans')
        .then(response => response.json())
        .then(scans => {
            // Take most recent 5 scans
            const recentScans = scans.slice(0, 5);
            
            // Clear table if this is a full refresh
            if (recentScans.length > 0) {
                tableElement.innerHTML = '';
            }
            
            // Populate table
            recentScans.forEach(scan => {
                addRecentScan({
                    id: scan.id,
                    name: scan.name,
                    target: scan.target,
                    status: scan.status,
                    progress: scan.progress
                });
            });
        })
        .catch(error => {
            console.error('Error loading scans:', error);
        });
}

/**
 * Set up WebSocket connection for real-time updates
 */
function startWebSocketConnection() {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${wsProtocol}//${window.location.host}/ws`;
    
    const socket = new WebSocket(wsUrl);
    
    socket.onopen = function(e) {
        console.log('WebSocket connection established');
    };
    
    socket.onmessage = function(event) {
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
        }
    };
    
    socket.onclose = function(event) {
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
        if (socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({type: 'ping'}));
        }
    }, 30000);
}

/**
 * Add a new notification to the dropdown
 */
function addNotification(notification) {
    const container = document.getElementById('notificationsContainer');
    
    if (!container) return;
    
    const notificationItem = document.createElement('li');
    notificationItem.classList.add('notification-item', 'unread');
    
    if (notification.severity === 'critical') {
        notificationItem.classList.add('critical');
    }
    
    // Determine icon class based on notification type
    let iconClass = 'bi-info-circle-fill';
    if (notification.type === 'alert') iconClass = 'bi-exclamation-triangle-fill';
    if (notification.type === 'warning') iconClass = 'bi-exclamation-circle-fill';
    
    notificationItem.innerHTML = `
        <div class="notification-icon">
            <i class="${iconClass}"></i>
        </div>
        <div class="notification-content">
            <div class="notification-message">${notification.message}</div>
            <div class="notification-time">Just now</div>
        </div>
    `;
    
    // Add to the beginning
    container.insertBefore(notificationItem, container.firstChild);
    
    // Update badge count
    const badge = document.querySelector('.notification-badge');
    if (badge) {
        const currentCount = parseInt(badge.textContent);
        badge.textContent = currentCount + 1;
    }
}
