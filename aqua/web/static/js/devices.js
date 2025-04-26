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
        if (device.type.toLowerCase().includes('camera')) iconClass = 'bi-camera-video';
        if (device.type.toLowerCase().includes('router')) iconClass = 'bi-router';
        if (device.type.toLowerCase().includes('speaker')) iconClass = 'bi-speaker';
        if (device.type.toLowerCase().includes('lock')) iconClass = 'bi-lock';
        if (device.type.toLowerCase().includes('thermostat')) iconClass = 'bi-thermometer';
        
        // Determine color based on risk score
        let colorClass = 'bg-green';
        if (device.risk_score > 40) colorClass = 'bg-yellow';
        if (device.risk_score > 70) colorClass = 'bg-red';
        
        // Calculate online status
        const isOnline = true; // placeholder: this would come from device data
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
                        <div class="fw-medium">${device.type} - ${device.id}</div>
                        <div class="small text-muted">${device.manufacturer}</div>
                    </div>
                </div>
            </td>
            <td>${device.ip}</td>
            <td>${device.type}</td>
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
                ${device.vulnerabilities > 0 ? `<span class="badge bg-danger ms-1">${device.vulnerabilities}</span>` : ''}
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
    
    const vulnerableDevices = devices.filter(d => d.vulnerabilities > 0);
    document.getElementById('vulnerableDevicesCount').textContent = vulnerableDevices.length;
    
    // For demo, we'll assume all are online
    document.getElementById('onlineDevicesCount').textContent = devices.length;
    document.getElementById('offlineDevicesCount').textContent = '0';
}

/**
 * Initialize device distribution chart
 */
function initDeviceDistributionChart() {
    const chartElement = document.getElementById('deviceDistributionChart');
    
    if (!chartElement) return;
    
    fetch('/api/devices')
        .then(response => response.json())
        .then(devices => {
            // Count devices by type
            const deviceTypes = {};
            devices.forEach(device => {
                if (!deviceTypes[device.type]) {
                    deviceTypes[device.type] = 0;
                }
                deviceTypes[device.type]++;
            });
            
            // Prepare chart data
            const labels = Object.keys(deviceTypes);
            const data = Object.values(deviceTypes);
            const colors = ['#2c7be5', '#e63757', '#00b274', '#f6c343', '#fd7e14', '#6b5eae', '#39afd1'];
            
            // Create chart
            const options = {
                series: data,
                chart: {
                    type: 'pie',
                    height: 300,
                    toolbar: {
                        show: false
                    }
                },
                labels: labels,
                colors: colors,
                legend: {
                    position: 'bottom'
                },
                responsive: [{
                    breakpoint: 480,
                    options: {
                        chart: {
                            height: 300
                        },
                        legend: {
                            position: 'bottom'
                        }
                    }
                }]
            };
            
            const chart = new ApexCharts(chartElement, options);
            chart.render();
        })
        .catch(error => {
            console.error('Error loading device distribution data:', error);
        });
}

/**
 * Initialize risk distribution chart
 */
function initRiskDistributionChart() {
    const chartElement = document.getElementById('riskDistributionChart');
    
    if (!chartElement) return;
    
    fetch('/api/devices')
        .then(response => response.json())
        .then(devices => {
            // Group by risk category
            const riskCategories = {
                'High Risk (70-100)': 0,
                'Medium Risk (40-69)': 0,
                'Low Risk (0-39)': 0
            };
            
            devices.forEach(device => {
                if (device.risk_score >= 70) {
                    riskCategories['High Risk (70-100)']++;
                } else if (device.risk_score >= 40) {
                    riskCategories['Medium Risk (40-69)']++;
                } else {
                    riskCategories['Low Risk (0-39)']++;
                }
            });
            
            // Prepare chart data
            const labels = Object.keys(riskCategories);
            const data = Object.values(riskCategories);
            const colors = ['#e63757', '#f6c343', '#00b274'];
            
            // Create chart
            const options = {
                series: data,
                chart: {
                    type: 'donut',
                    height: 300,
                    toolbar: {
                        show: false
                    }
                },
                labels: labels,
                colors: colors,
                dataLabels: {
                    enabled: true
                },
                legend: {
                    position: 'bottom'
                },
                responsive: [{
                    breakpoint: 480,
                    options: {
                        chart: {
                            height: 300
                        },
                        legend: {
                            position: 'bottom'
                        }
                    }
                }]
            };
            
            const chart = new ApexCharts(chartElement, options);
            chart.render();
        })
        .catch(error => {
            console.error('Error loading risk distribution data:', error);
        });
}

/**
 * Set up device filters
 */
function setupDeviceFilters() {
    // Add filter change handlers
    const filters = document.querySelectorAll('#deviceTypeFilter, #manufacturerFilter, #riskFilter, #statusFilter');
    filters.forEach(filter => {
        filter.addEventListener('change', function() {
            // This would filter the device table based on selected values
            console.log('Filter applied:', this.id, this.value);
            // In a real implementation, this would re-fetch or filter the device list
        });
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
