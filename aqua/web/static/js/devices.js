/**
 * Aqua IoT Security Platform
 * Devices Page Functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Load device data
    loadDevices();
    
    // Initialize device charts
    initDeviceDistributionChart();
    initRiskDistributionChart();
    
    // Set up event listeners
    setupDeviceFilters();
    setupDeviceSearch();
    setupDeviceSelectionHandlers();
    setupDeviceFormHandlers();
});

/**
 * Load devices from API and populate table
 */
function loadDevices() {
    // Show loading state
    document.getElementById('deviceInventoryTable').innerHTML = `
        <tr>
            <td colspan="9" class="text-center py-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">Loading devices...</p>
            </td>
        </tr>
    `;
    
    // Fetch devices from API
    fetch('/api/devices')
        .then(response => response.json())
        .then(devices => {
            // Update stats
            updateDeviceStats(devices);
            
            // Populate table
            populateDeviceTable(devices);
        })
        .catch(error => {
            console.error('Error loading devices:', error);
            document.getElementById('deviceInventoryTable').innerHTML = `
                <tr>
                    <td colspan="9" class="text-center py-4">
                        <div class="alert alert-danger">
                            Failed to load devices. Please try again.
                        </div>
                    </td>
                </tr>
            `;
        });
}

/**
 * Load demo device data
 */
function loadDemoDevices() {
    const devices = [
        {
            id: "dev_1",
            ip: "192.168.1.101",
            hostname: "iot-camera-01",
            mac: "AA:BB:CC:DD:EE:01",
            device_type: "camera",
            manufacturer: "SecurityCam",
            model: "SC-2000",
            firmware_version: "1.2.3",
            is_online: true,
            open_ports: [80, 443, 8080],
            protocols: ["HTTP", "HTTPS", "RTSP"],
            services: {"80": "HTTP", "443": "HTTPS", "8080": "HTTP-alt"},
            vulnerabilities: [
                {
                    id: "vuln_1",
                    name: "Default Credentials",
                    description: "Device uses default login credentials",
                    severity: "high"
                }
            ]
        },
        {
            id: "dev_2",
            ip: "192.168.1.102",
            hostname: "smart-thermostat",
            mac: "AA:BB:CC:DD:EE:02",
            device_type: "thermostat",
            manufacturer: "SmartHome",
            model: "TH-2000",
            firmware_version: "2.1.0",
            is_online: true,
            open_ports: [80, 1883],
            protocols: ["HTTP", "MQTT"],
            services: {"80": "HTTP", "1883": "MQTT"},
            vulnerabilities: [
                {
                    id: "vuln_2",
                    name: "Unencrypted MQTT",
                    description: "Device uses unencrypted MQTT protocol",
                    severity: "medium"
                }
            ]
        },
        {
            id: "dev_3",
            ip: "192.168.1.103",
            hostname: "smart-lock",
            mac: "AA:BB:CC:DD:EE:03",
            device_type: "lock",
            manufacturer: "SecureLock",
            model: "SL-500",
            firmware_version: "0.9.4",
            is_online: true,
            open_ports: [80, 443, 5683],
            protocols: ["HTTP", "HTTPS", "CoAP"],
            services: {"80": "HTTP", "443": "HTTPS", "5683": "CoAP"},
            vulnerabilities: [
                {
                    id: "vuln_3",
                    name: "Outdated Firmware",
                    description: "Device is running outdated firmware with known vulnerabilities",
                    severity: "high"
                }
            ]
        },
        {
            id: "dev_4",
            ip: "192.168.1.104",
            hostname: "router",
            mac: "AA:BB:CC:DD:EE:04",
            device_type: "router",
            manufacturer: "NetLink",
            model: "NL-1200",
            firmware_version: "3.4.2",
            is_online: true,
            open_ports: [80, 443, 22, 23],
            protocols: ["HTTP", "HTTPS", "SSH", "Telnet"],
            services: {"80": "HTTP", "443": "HTTPS", "22": "SSH", "23": "Telnet"},
            vulnerabilities: [
                {
                    id: "vuln_5",
                    name: "Open Telnet Port",
                    description: "Device has open Telnet port which is insecure",
                    severity: "critical"
                }
            ]
        }
    ];

    // Process the demo data
    updateDeviceStats(devices);
    populateDeviceTable(devices);
    updateDeviceDistributionChart(devices);
    updateRiskDistributionChart(devices);
}

/**
 * Populate device inventory table
 */
function populateDeviceTable(devices) {
    const tableBody = document.getElementById('deviceInventoryTable');
    
    // Clear table body
    tableBody.innerHTML = '';
    
    // Check if we have devices
    if (devices.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="9" class="text-center py-4">
                    <div class="alert alert-info">
                        No devices found. Add your first device to get started.
                    </div>
                </td>
            </tr>
        `;
        return;
    }
    
    // Add rows for each device
    devices.forEach(device => {
        const row = document.createElement('tr');
        row.setAttribute('data-device-id', device.id);
        
        // Determine icon based on device type
        let iconClass = 'bi-hdd';
        if (device.device_type.toLowerCase().includes('camera')) iconClass = 'bi-camera-video';
        if (device.device_type.toLowerCase().includes('router')) iconClass = 'bi-router';
        if (device.device_type.toLowerCase().includes('speaker')) iconClass = 'bi-speaker';
        if (device.device_type.toLowerCase().includes('lock')) iconClass = 'bi-lock';
        if (device.device_type.toLowerCase().includes('thermostat')) iconClass = 'bi-thermometer';
        
        // Determine color based on risk score
        let colorClass = 'bg-green';
        if (device.risk_score > 40) colorClass = 'bg-yellow';
        if (device.risk_score > 70) colorClass = 'bg-red';
        
        // Calculate online status
        const isOnline = device.is_online !== false;
        const statusBadge = isOnline ? 
            '<span class="badge bg-success">Online</span>' : 
            '<span class="badge bg-secondary">Offline</span>';
        
        row.innerHTML = `
            <td>
                <div class="form-check">
                    <input class="form-check-input device-checkbox" type="checkbox" value="${device.id}">
                </div>
            </td>
            <td>
                <div class="device-name">
                    <div class="device-icon ${colorClass}">
                        <i class="bi ${iconClass}"></i>
                    </div>
                    <div>
                        <div class="fw-medium">${device.device_type} - ${device.id}</div>
                        <div class="small text-muted">${device.manufacturer}</div>
                    </div>
                </div>
            </td>
            <td>${device.ip}</td>
            <td>${device.device_type}</td>
            <td>${device.manufacturer}</td>
            <td>Just now</td>
            <td>
                <div class="d-flex align-items-center">
                    <span class="fw-medium me-2">${device.risk_score}</span>
                    <div class="progress flex-grow-1" style="height: 5px;">
                        <div class="progress-bar ${colorClass}" role="progressbar" style="width: ${device.risk_score}%"></div>
                    </div>
                </div>
            </td>
            <td>
                ${statusBadge}
                ${device.vulnerabilities.length > 0 ? `<span class="badge bg-danger ms-1">${device.vulnerabilities.length}</span>` : ''}
            </td>
            <td>
                <div class="dropdown">
                    <button class="btn btn-sm btn-outline-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown">
                        Actions
                    </button>
                    <ul class="dropdown-menu">
                        <li><a class="dropdown-item" href="#">View Details</a></li>
                        <li><a class="dropdown-item" href="#">Run Scan</a></li>
                        <li><a class="dropdown-item" href="#">Edit Device</a></li>
                        <li><hr class="dropdown-divider"></li>
                        <li><a class="dropdown-item text-danger" href="#">Delete Device</a></li>
                    </ul>
                </div>
            </td>
        `;
        
        tableBody.appendChild(row);
    });
}

/**
 * Update device stats based on loaded devices
 */
function updateDeviceStats(devices) {
    document.getElementById('totalDevicesCount').textContent = devices.length;
    
    const vulnerableDevices = devices.filter(d => d.vulnerabilities.length > 0);
    document.getElementById('vulnerableDevicesCount').textContent = vulnerableDevices.length;
    
    const onlineDevices = devices.filter(d => d.is_online !== false).length;
    document.getElementById('onlineDevicesCount').textContent = onlineDevices;
    document.getElementById('offlineDevicesCount').textContent = devices.length - onlineDevices;
}

/**
 * Initialize device distribution chart
 */
function initDeviceDistributionChart() {
    const chartElement = document.getElementById('deviceDistributionChart');
    
    if (!chartElement) return;
    
    const options = {
        series: [10, 8, 6, 5, 4, 5],
        chart: {
            type: 'pie',
            height: 300,
            toolbar: {
                show: false
            }
        },
        labels: ['Camera', 'Smart Speaker', 'Thermostat', 'Router', 'Lock', 'Other'],
        colors: ['#2c7be5', '#6b5eae', '#00b274', '#f6c343', '#e63757', '#95aac9'],
        legend: {
            position: 'bottom'
        },
        responsive: [{
            breakpoint: 480,
            options: {
                chart: {
                    height: 200
                },
                legend: {
                    position: 'bottom'
                }
            }
        }]
    };
    
    window.deviceDistributionChart = new ApexCharts(chartElement, options);
    window.deviceDistributionChart.render();
}

/**
 * Update device distribution chart with real data
 */
function updateDeviceDistributionChart(devices) {
    if (!window.deviceDistributionChart) return;
    
    // Count devices by type
    const typeCounts = {};
    
    devices.forEach(device => {
        const type = device.device_type || 'Unknown';
        typeCounts[type] = (typeCounts[type] || 0) + 1;
    });
    
    // Get top 5 types + "Other"
    const sortedTypes = Object.entries(typeCounts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5);
    
    const otherCount = devices.length - sortedTypes.reduce((sum, [_, count]) => sum + count, 0);
    
    // Prepare data for chart
    const labels = sortedTypes.map(([type]) => type.charAt(0).toUpperCase() + type.slice(1));
    const series = sortedTypes.map(([_, count]) => count);
    
    if (otherCount > 0) {
        labels.push('Other');
        series.push(otherCount);
    }
    
    // Update chart
    window.deviceDistributionChart.updateOptions({
        labels: labels
    });
    window.deviceDistributionChart.updateSeries(series);
}

/**
 * Initialize risk distribution chart
 */
function initRiskDistributionChart() {
    const chartElement = document.getElementById('riskDistributionChart');
    
    if (!chartElement) return;
    
    const options = {
        series: [5, 8, 12, 15],
        chart: {
            type: 'donut',
            height: 300,
            toolbar: {
                show: false
            }
        },
        labels: ['Critical', 'High', 'Medium', 'Low'],
        colors: ['#e63757', '#f6c343', '#00b274', '#2c7be5'],
        legend: {
            position: 'bottom'
        },
        responsive: [{
            breakpoint: 480,
            options: {
                chart: {
                    height: 200
                },
                legend: {
                    position: 'bottom'
                }
            }
        }]
    };
    
    window.riskDistributionChart = new ApexCharts(chartElement, options);
    window.riskDistributionChart.render();
}

/**
 * Update risk distribution chart with real data
 */
function updateRiskDistributionChart(devices) {
    if (!window.riskDistributionChart) return;
    
    // Count devices by risk level
    let criticalCount = 0;
    let highCount = 0;
    let mediumCount = 0;
    let lowCount = 0;
    
    devices.forEach(device => {
        const vulns = device.vulnerabilities || [];
        if (vulns.some(v => v.severity === 'critical')) {
            criticalCount++;
        } else if (vulns.some(v => v.severity === 'high')) {
            highCount++;
        } else if (vulns.some(v => v.severity === 'medium')) {
            mediumCount++;
        } else if (vulns.some(v => v.severity === 'low')) {
            lowCount++;
        } else {
            lowCount++;
        }
    });
    
    // Update chart
    window.riskDistributionChart.updateSeries([criticalCount, highCount, mediumCount, lowCount]);
}

/**
 * Set up device filters
 */
function setupDeviceFilters() {
    const filterButtons = document.querySelectorAll('.device-filter');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from all buttons
            filterButtons.forEach(btn => btn.classList.remove('active'));
            
            // Add active class to clicked button
            this.classList.add('active');
            
            // Apply filter
            filterDevices(this.getAttribute('data-filter'));
        });
    });
}

/**
 * Filter device table
 */
function filterDevices(filter = 'all') {
    const rows = document.querySelectorAll('#deviceInventoryTable tr');
    
    rows.forEach(row => {
        const statusBadge = row.querySelector('.badge');
        const riskBadge = row.querySelectorAll('.badge')[1];
        
        switch (filter) {
            case 'online':
                row.style.display = statusBadge?.textContent === 'Online' ? '' : 'none';
                break;
            case 'offline':
                row.style.display = statusBadge?.textContent === 'Offline' ? '' : 'none';
                break;
            case 'vulnerable':
                row.style.display = riskBadge?.textContent !== 'Low' ? '' : 'none';
                break;
            default:
                row.style.display = '';
                break;
        }
    });
}

/**
 * Set up device search functionality
 */
function setupDeviceSearch() {
    const searchInput = document.getElementById('deviceSearch');
    if (!searchInput) return;
    
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        const rows = document.querySelectorAll('#deviceInventoryTable tr');
        
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(searchTerm) ? '' : 'none';
        });
    });
}

/**
 * Set up device selection handlers for bulk actions
 */
function setupDeviceSelectionHandlers() {
    const selectAllCheckbox = document.getElementById('selectAllDevices');
    const bulkActionButtons = document.querySelectorAll('.bulk-action-btn');
    
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const checkboxes = document.querySelectorAll('.device-checkbox');
            checkboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
            
            updateBulkActionButtons();
        });
    }
    
    // Individual checkbox change handler
    document.addEventListener('change', function(e) {
        if (e.target && e.target.classList.contains('device-checkbox')) {
            updateBulkActionButtons();
        }
    });
    
    // Update bulk action button state
    function updateBulkActionButtons() {
        const checkedBoxes = document.querySelectorAll('.device-checkbox:checked');
        bulkActionButtons.forEach(button => {
            button.disabled = checkedBoxes.length === 0;
        });
    }
}

/**
 * Set up device form handlers
 */
function setupDeviceFormHandlers() {
    // Add device form handler
    const saveDeviceBtn = document.getElementById('saveDeviceBtn');
    if (saveDeviceBtn) {
        saveDeviceBtn.addEventListener('click', function() {
            const form = document.getElementById('addDeviceForm');
            
            // Basic validation
            if (!form.checkValidity()) {
                form.reportValidity();
                return;
            }
            
            // Collect form data
            const deviceData = {
                name: document.getElementById('deviceName').value,
                ip: document.getElementById('deviceIp').value,
                type: document.getElementById('deviceType').value,
                manufacturer: document.getElementById('deviceManufacturer').value,
                mac: document.getElementById('deviceMac').value,
                tags: document.getElementById('deviceTags').value.split(',').map(tag => tag.trim())
            };
            
            // In a real implementation, this would submit to an API
            console.log('Device data to save:', deviceData);
            
            // Close modal and show success message
            const modal = bootstrap.Modal.getInstance(document.getElementById('addDeviceModal'));
            modal.hide();
            
            showToast('Device added successfully!', 'success');
            
            // Refresh device list
            loadDevices();
        });
    }
}
