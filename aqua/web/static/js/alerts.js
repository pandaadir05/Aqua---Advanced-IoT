/**
 * Aqua IoT Security Platform
 * Alerts Page Functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize charts
    initAlertTrendsChart();
    initAlertCategoriesChart();
    
    // Load alerts data
    loadAlerts();
    
    // Set up event listeners
    setupAlertSearch();
    setupAlertDetailModal();
    setupFilterControls();
    
    // Set up refresh button
    const refreshAlertsBtn = document.getElementById('refreshAlertsBtn');
    if (refreshAlertsBtn) {
        refreshAlertsBtn.addEventListener('click', function() {
            loadAlerts();
        });
    }
});

/**
 * Load alerts data and populate table
 */
function loadAlerts() {
    const alertsTable = document.getElementById('alertsTable');
    
    if (!alertsTable) return;
    
    // Show loading state
    alertsTable.innerHTML = `
        <tr>
            <td colspan="7" class="text-center py-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">Loading alerts...</p>
            </td>
        </tr>
    `;
    
    // Demo alerts data - in a real app this would come from an API
    const alerts = [
        { id: 'alert001', title: 'Unauthorized Access Attempt', device: { id: 'dev001', name: 'Camera', ip: '192.168.1.101' }, severity: 'critical', status: 'open', timestamp: '2023-11-02T14:28:05Z' },
        { id: 'alert002', title: 'Outdated Firmware', device: { id: 'dev004', name: 'Router', ip: '192.168.1.1' }, severity: 'high', status: 'open', timestamp: '2023-11-02T12:15:22Z' },
        { id: 'alert003', title: 'Unusual Traffic Pattern', device: { id: 'dev001', name: 'Camera', ip: '192.168.1.101' }, severity: 'medium', status: 'in_progress', timestamp: '2023-11-02T09:42:17Z' },
        { id: 'alert004', title: 'Device Disconnected', device: { id: 'dev005', name: 'Smart Lock', ip: '192.168.1.104' }, severity: 'low', status: 'resolved', timestamp: '2023-11-01T22:03:49Z' },
        { id: 'alert005', title: 'Port Scan Detected', device: { id: 'dev001', name: 'Camera', ip: '192.168.1.101' }, severity: 'high', status: 'open', timestamp: '2023-11-01T20:17:33Z' },
        { id: 'alert006', title: 'Weak Encryption', device: { id: 'dev002', name: 'Smart Speaker', ip: '192.168.1.102' }, severity: 'medium', status: 'open', timestamp: '2023-11-01T18:45:11Z' },
        { id: 'alert007', title: 'Failed Login Attempts', device: { id: 'dev003', name: 'Thermostat', ip: '192.168.1.103' }, severity: 'high', status: 'in_progress', timestamp: '2023-11-01T15:27:58Z' },
        { id: 'alert008', title: 'Default Credentials Used', device: { id: 'dev002', name: 'Smart Speaker', ip: '192.168.1.102' }, severity: 'critical', status: 'open', timestamp: '2023-11-01T12:19:24Z' },
        { id: 'alert009', title: 'Suspicious Process', device: { id: 'dev004', name: 'Router', ip: '192.168.1.1' }, severity: 'high', status: 'resolved', timestamp: '2023-11-01T09:05:17Z' },
        { id: 'alert010', title: 'Firmware Update Available', device: { id: 'dev003', name: 'Thermostat', ip: '192.168.1.103' }, severity: 'low', status: 'open', timestamp: '2023-10-31T21:37:42Z' }
    ];
    
    // Update summary counts
    updateAlertCounts(alerts);
    
    // Clear and populate table
    alertsTable.innerHTML = '';
    
    // Add alerts to table
    alerts.forEach(alert => {
        // Create table row
        const row = document.createElement('tr');
        row.setAttribute('data-alert-id', alert.id);
        
        // Determine severity icon and class
        let severityIcon, severityClass;
        switch(alert.severity) {
            case 'critical':
                severityIcon = 'bi-exclamation-octagon-fill';
                severityClass = 'badge-critical';
                break;
            case 'high':
                severityIcon = 'bi-exclamation-triangle-fill';
                severityClass = 'badge-high';
                break;
            case 'medium':
                severityIcon = 'bi-exclamation-circle-fill';
                severityClass = 'badge-medium';
                break;
            default:
                severityIcon = 'bi-info-circle-fill';
                severityClass = 'badge-low';
        }
        
        // Determine status badge
        let statusBadge;
        switch(alert.status) {
            case 'in_progress':
                statusBadge = '<span class="badge bg-primary">In Progress</span>';
                break;
            case 'resolved':
                statusBadge = '<span class="badge bg-success">Resolved</span>';
                break;
            case 'false_positive':
                statusBadge = '<span class="badge bg-secondary">False Positive</span>';
                break;
            default:
                statusBadge = '<span class="badge bg-danger">Open</span>';
        }
        
        // Format timestamp
        const alertDate = new Date(alert.timestamp);
        const timeAgo = formatTimeAgo(alertDate);
        
        // Build row content
        row.innerHTML = `
            <td>
                <div class="severity-indicator ${alert.severity}"></div>
            </td>
            <td>
                <div class="fw-medium">${alert.title}</div>
                <div class="small text-muted">Alert ID: ${alert.id}</div>
            </td>
            <td>
                <div class="fw-medium">${alert.device.name}</div>
                <div class="small text-muted">${alert.device.ip}</div>
            </td>
            <td><span class="badge ${severityClass}">${alert.severity.charAt(0).toUpperCase() + alert.severity.slice(1)}</span></td>
            <td>${statusBadge}</td>
            <td>
                <div>${alertDate.toLocaleDateString()}</div>
                <div class="small text-muted">${timeAgo}</div>
            </td>
            <td>
                <button class="btn btn-sm btn-outline-primary view-alert-btn" data-alert-id="${alert.id}">
                    View
                </button>
            </td>
        `;
        
        alertsTable.appendChild(row);
    });
    
    // Add click event for alert view buttons
    const viewButtons = document.querySelectorAll('.view-alert-btn');
    viewButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const alertId = this.getAttribute('data-alert-id');
            openAlertDetailModal(alertId);
        });
    });
}

/**
 * Update alert count statistics
 */
function updateAlertCounts(alerts) {
    document.getElementById('criticalAlertsCount').textContent = alerts.filter(a => a.severity === 'critical').length;
    document.getElementById('highAlertsCount').textContent = alerts.filter(a => a.severity === 'high').length;
    document.getElementById('mediumAlertsCount').textContent = alerts.filter(a => a.severity === 'medium').length;
    document.getElementById('lowAlertsCount').textContent = alerts.filter(a => a.severity === 'low').length;
}

/**
 * Initialize alert trends chart
 */
function initAlertTrendsChart() {
    const chartElement = document.getElementById('alertTrendsChart');
    
    if (!chartElement) return;
    
    // Generate dates for the past week
    const dates = [];
    for (let i = 6; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        dates.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
    }
    
    // Generate demo data for the chart
    const options = {
        series: [
            {
                name: 'Critical',
                data: [2, 1, 3, 2, 0, 1, 2]
            },
            {
                name: 'High',
                data: [4, 3, 5, 2, 6, 4, 3]
            },
            {
                name: 'Medium',
                data: [7, 6, 4, 8, 5, 6, 5]
            },
            {
                name: 'Low',
                data: [3, 2, 5, 4, 3, 5, 4]
            }
        ],
        chart: {
            type: 'bar',
            height: 300,
            stacked: true,
            toolbar: {
                show: false
            }
        },
        plotOptions: {
            bar: {
                horizontal: false,
                columnWidth: '55%',
            },
        },
        colors: ['#e63757', '#fd7e14', '#f6c343', '#39afd1'],
        dataLabels: {
            enabled: false
        },
        xaxis: {
            categories: dates,
        },
        legend: {
            position: 'top',
            horizontalAlign: 'right'
        },
        fill: {
            opacity: 1
        },
        tooltip: {
            y: {
                formatter: function (val) {
                    return val + " alerts";
                }
            }
        }
    };
    
    const chart = new ApexCharts(chartElement, options);
    chart.render();
}

/**
 * Initialize alert categories chart
 */
function initAlertCategoriesChart() {
    const chartElement = document.getElementById('alertCategoriesChart');
    
    if (!chartElement) return;
    
    const options = {
        series: [30, 25, 15, 12, 10, 8],
        chart: {
            type: 'donut',
            height: 300,
            toolbar: {
                show: false
            }
        },
        labels: ['Authentication', 'Network', 'Configuration', 'Firmware', 'Access Control', 'Other'],
        colors: ['#2c7be5', '#e63757', '#00b274', '#f6c343', '#6b5eae', '#95aac9'],
        legend: {
            show: true,
            position: 'bottom',
            horizontalAlign: 'center'
        },
        dataLabels: {
            enabled: false
        },
        plotOptions: {
            pie: {
                donut: {
                    size: '65%'
                }
            }
        }
    };
    
    const chart = new ApexCharts(chartElement, options);
    chart.render();
}

/**
 * Setup alert search functionality
 */
function setupAlertSearch() {
    const searchInput = document.getElementById('alertSearch');
    const searchBtn = document.getElementById('searchAlertsBtn');
    
    if (searchInput && searchBtn) {
        searchBtn.addEventListener('click', function() {
            const searchTerm = searchInput.value.toLowerCase();
            filterAlerts(searchTerm);
        });
        
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                const searchTerm = searchInput.value.toLowerCase();
                filterAlerts(searchTerm);
            }
        });
    }
}

/**
 * Filter alerts based on search term
 */
function filterAlerts(searchTerm) {
    const rows = document.querySelectorAll('#alertsTable tr');
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        if (text.includes(searchTerm)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

/**
 * Setup alert detail modal functionality
 */
function setupAlertDetailModal() {
    const saveAlertBtn = document.getElementById('saveAlertBtn');
    
    if (saveAlertBtn) {
        saveAlertBtn.addEventListener('click', function() {
            // Get updated values
            const status = document.getElementById('alertDetailStatus').value;
            const assignedTo = document.getElementById('alertDetailAssigned').value;
            const notes = document.getElementById('alertDetailNotes').value;
            
            // In a real app, this would save to an API
            console.log('Saving alert update:', { status, assignedTo, notes });
            
            // Show success message
            showToast('Alert updated successfully', 'success');
            
            // Close the modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('alertDetailModal'));
            modal.hide();
            
            // Refresh alerts list
            loadAlerts();
        });
    }
}

/**
 * Open alert detail modal
 */
function openAlertDetailModal(alertId) {
    // In a real app, this would fetch alert details from an API
    // For demo, we'll use hardcoded data based on alertId
    
    // Setup modal content
    document.getElementById('alertDetailTitle').textContent = 'Unauthorized Access Attempt';
    document.getElementById('alertDetailSeverity').innerHTML = '<i class="bi bi-exclamation-triangle me-2"></i> Critical';
    document.getElementById('alertDetailSeverity').className = 'alert-severity-badge critical';
    document.getElementById('alertDetailTime').textContent = 'Nov 2, 2023 14:28:05';
    document.getElementById('alertDetailDevice').textContent = 'Camera (192.168.1.101)';
    document.getElementById('alertDetailDescription').textContent = 'Multiple failed login attempts detected on the device from IP address 192.168.1.35.';
    document.getElementById('alertDetailStatus').value = 'Open';
    document.getElementById('alertDetailAssigned').value = '';
    document.getElementById('alertDetailNotes').value = '';
    
    // Technical details - this would be dynamic in a real app
    document.getElementById('alertDetailTechnical').textContent = JSON.stringify({
        "source_ip": "192.168.1.35",
        "destination_ip": "192.168.1.101",
        "destination_port": 22,
        "protocol": "SSH",
        "attempts": 5,
        "usernames": ["admin", "root"],
        "timestamp": "2023-11-02T14:28:05Z"
    }, null, 2);
    
    // Show the modal
    const modal = new bootstrap.Modal(document.getElementById('alertDetailModal'));
    modal.show();
}

/**
 * Setup filter controls
 */
function setupFilterControls() {
    const applyFiltersBtn = document.getElementById('applyFiltersBtn');
    const resetFiltersBtn = document.getElementById('resetFiltersBtn');
    
    if (applyFiltersBtn) {
        applyFiltersBtn.addEventListener('click', function() {
            // Get filter values
            const criticalChecked = document.getElementById('criticalFilter').checked;
            const highChecked = document.getElementById('highFilter').checked;
            const mediumChecked = document.getElementById('mediumFilter').checked;
            const lowChecked = document.getElementById('lowFilter').checked;
            
            const openChecked = document.getElementById('openFilter').checked;
            const inProgressChecked = document.getElementById('inProgressFilter').checked;
            const resolvedChecked = document.getElementById('resolvedFilter').checked;
            
            const timeRange = document.getElementById('timeRangeSelect').value;
            
            // Filter alerts based on selected filters
            // In a real app, this would call an API with filter parameters
            console.log('Applying filters:', {
                severity: { critical: criticalChecked, high: highChecked, medium: mediumChecked, low: lowChecked },
                status: { open: openChecked, inProgress: inProgressChecked, resolved: resolvedChecked },
                timeRange: timeRange
            });
            
            // For demo, just reload alerts
            loadAlerts();
            
            // Close the dropdown
            document.getElementById('alertFilterDropdown').click();
        });
    }
    
    if (resetFiltersBtn) {
        resetFiltersBtn.addEventListener('click', function() {
            // Reset all filter checkboxes to checked
            document.getElementById('criticalFilter').checked = true;
            document.getElementById('highFilter').checked = true;
            document.getElementById('mediumFilter').checked = true;
            document.getElementById('lowFilter').checked = true;
            
            document.getElementById('openFilter').checked = true;
            document.getElementById('inProgressFilter').checked = true;
            document.getElementById('resolvedFilter').checked = false;
            
            // Reset time range to default
            document.getElementById('timeRangeSelect').value = 'week';
            
            // Reload alerts with default filters
            loadAlerts();
        });
    }
}
