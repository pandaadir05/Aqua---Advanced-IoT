/**
 * Aqua IoT Security Platform
 * Alerts Page Functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing alerts page');
    
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
            showToast('Alerts refreshed', 'success');
        });
    }
});

/**
 * Load alerts data from API
 */
function loadAlerts() {
    const alertsTableBody = document.getElementById('alertsTableBody');
    if (!alertsTableBody) return;
    
    // Show loading state
    alertsTableBody.innerHTML = `
        <tr>
            <td colspan="6" class="text-center py-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">Loading alerts...</p>
            </td>
        </tr>
    `;
    
    // Fetch alerts from API
    fetch('/api/alerts')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(alerts => {
            console.log('Loaded alerts:', alerts);
            
            // Update alert count statistics
            updateAlertCounts(alerts);
            
            // Populate table
            populateAlertsTable(alerts);
        })
        .catch(error => {
            console.error('Error loading alerts:', error);
            alertsTableBody.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center py-4">
                        <div class="alert alert-danger">
                            Failed to load alerts. Please try again.
                        </div>
                    </td>
                </tr>
            `;
        });
}

/**
 * Update alert count statistics
 */
function updateAlertCounts(alerts) {
    const criticalCount = document.getElementById('criticalAlertCount');
    const highCount = document.getElementById('highAlertCount');
    const mediumCount = document.getElementById('mediumAlertCount');
    const lowCount = document.getElementById('lowAlertCount');
    
    if (criticalCount) criticalCount.textContent = alerts.filter(a => a.severity === 'critical').length;
    if (highCount) highCount.textContent = alerts.filter(a => a.severity === 'high').length;
    if (mediumCount) mediumCount.textContent = alerts.filter(a => a.severity === 'medium').length;
    if (lowCount) lowCount.textContent = alerts.filter(a => a.severity === 'low').length;
}

/**
 * Populate alerts table with data
 */
function populateAlertsTable(alerts) {
    const alertsTableBody = document.getElementById('alertsTableBody');
    if (!alertsTableBody) return;
    
    // Clear table body
    alertsTableBody.innerHTML = '';
    
    // Check if we have alerts
    if (!alerts || alerts.length === 0) {
        alertsTableBody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center py-4">
                    <div class="alert alert-info">
                        No alerts found.
                    </div>
                </td>
            </tr>
        `;
        return;
    }
    
    // Add rows for each alert
    alerts.forEach(alert => {
        const row = document.createElement('tr');
        row.setAttribute('data-alert-id', alert.id);
        
        // Determine severity class
        let severityClass, severityIcon;
        switch(alert.severity) {
            case 'critical':
                severityClass = 'danger';
                severityIcon = 'bi-exclamation-octagon-fill';
                break;
            case 'high':
                severityClass = 'warning';
                severityIcon = 'bi-exclamation-triangle-fill';
                break;
            case 'medium':
                severityClass = 'info';
                severityIcon = 'bi-exclamation-circle-fill';
                break;
            default:
                severityClass = 'secondary';
                severityIcon = 'bi-info-circle-fill';
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
                <div class="severity-indicator bg-${severityClass}">
                    <i class="bi ${severityIcon}"></i>
                </div>
            </td>
            <td>
                <div class="fw-medium">${alert.title}</div>
                <div class="small text-muted">${alert.description?.substring(0, 50)}${alert.description?.length > 50 ? '...' : ''}</div>
            </td>
            <td>
                <div class="fw-medium">${alert.device.name}</div>
                <div class="small text-muted">${alert.device.ip}</div>
            </td>
            <td>
                <div>${formatDate(alertDate)}</div>
                <div class="small text-muted">${timeAgo}</div>
            </td>
            <td>${statusBadge}</td>
            <td>
                <button class="btn btn-sm btn-outline-primary view-alert-btn" data-alert-id="${alert.id}">
                    View
                </button>
            </td>
        `;
        
        alertsTableBody.appendChild(row);
    });
    
    // Add click event for view buttons
    document.querySelectorAll('.view-alert-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const alertId = this.getAttribute('data-alert-id');
            showAlertDetail(alertId);
        });
    });
}

/**
 * Format date
 */
function formatDate(date) {
    return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
    });
}

/**
 * Format time ago
 */
function formatTimeAgo(date) {
    const now = new Date();
    const diffMs = now - date;
    const diffSecs = Math.round(diffMs / 1000);
    const diffMins = Math.round(diffSecs / 60);
    const diffHours = Math.round(diffMins / 60);
    const diffDays = Math.round(diffHours / 24);
    
    if (diffSecs < 60) {
        return 'just now';
    } else if (diffMins < 60) {
        return `${diffMins} minute${diffMins !== 1 ? 's' : ''} ago`;
    } else if (diffHours < 24) {
        return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
    } else {
        return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
    }
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
    
    // Demo data for the chart
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
        }
    };
    
    try {
        const chart = new ApexCharts(chartElement, options);
        chart.render();
    } catch (error) {
        console.error('Error rendering alert trends chart:', error);
    }
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
    
    try {
        const chart = new ApexCharts(chartElement, options);
        chart.render();
    } catch (error) {
        console.error('Error rendering alert categories chart:', error);
    }
}

/**
 * Set up alert search functionality
 */
function setupAlertSearch() {
    const searchInput = document.getElementById('alertSearch');
    
    if (searchInput) {
        searchInput.addEventListener('keyup', function() {
            const searchTerm = this.value.toLowerCase();
            filterAlerts(searchTerm);
        });
    }
}

/**
 * Filter alerts based on search term
 */
function filterAlerts(searchTerm) {
    const rows = document.querySelectorAll('#alertsTableBody tr');
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(searchTerm) ? '' : 'none';
    });
}

/**
 * Set up alert detail modal
 */
function setupAlertDetailModal() {
    // Handle modal close events to prevent stale data
    const alertDetailModal = document.getElementById('alertDetailModal');
    
    if (alertDetailModal) {
        alertDetailModal.addEventListener('hidden.bs.modal', function() {
            // Clear modal data when closed
            document.getElementById('alertDetailId').textContent = '';
            document.getElementById('alertDetailDescription').textContent = '';
            document.getElementById('alertDetailTechnical').textContent = '';
            document.getElementById('alertDetailRecommendations').innerHTML = '';
        });
    }
}

/**
 * Show alert detail in modal
 */
function showAlertDetail(alertId) {
    console.log('Showing alert detail for:', alertId);
    
    fetch(`/api/alerts/${alertId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(alert => {
            console.log('Alert detail:', alert);
            
            // Populate modal with alert details
            document.getElementById('alertDetailId').textContent = alert.id;
            document.getElementById('alertDetailTitle').textContent = alert.title;
            
            const severityBadge = document.getElementById('alertDetailSeverity');
            severityBadge.textContent = alert.severity.charAt(0).toUpperCase() + alert.severity.slice(1);
            severityBadge.className = `badge bg-${getSeverityClass(alert.severity)}`;
            
            document.getElementById('alertDetailStatus').value = alert.status || 'open';
            document.getElementById('alertDetailDevice').textContent = `${alert.device.name} (${alert.device.ip})`;
            
            // Format timestamp
            const alertDate = new Date(alert.timestamp);
            document.getElementById('alertDetailTime').textContent = alertDate.toLocaleString();
            
            document.getElementById('alertDetailCategory').textContent = alert.category || 'General';
            document.getElementById('alertDetailDescription').textContent = alert.description || 'No description available';
            
            // Technical details
            const technicalDetails = document.getElementById('alertDetailTechnical');
            if (technicalDetails) {
                technicalDetails.textContent = alert.technical_details || 'No technical details available';
            }
            
            // Recommendations
            const recommendations = document.getElementById('alertDetailRecommendations');
            if (recommendations) {
                if (alert.recommendations && Array.isArray(alert.recommendations)) {
                    recommendations.innerHTML = alert.recommendations
                        .map(rec => `<li>${rec}</li>`)
                        .join('');
                } else {
                    recommendations.innerHTML = '<li>No recommendations available</li>';
                }
            }
            
            // Set up action buttons
            setupAlertActionButtons(alert);
            
            // Show the modal
            const modal = new bootstrap.Modal(document.getElementById('alertDetailModal'));
            modal.show();
        })
        .catch(error => {
            console.error('Error fetching alert details:', error);
            showToast('Failed to load alert details', 'danger');
        });
}

/**
 * Set up action buttons in the alert detail modal
 */
function setupAlertActionButtons(alert) {
    // Block connection button
    const blockConnectionBtn = document.getElementById('blockConnectionBtn');
    if (blockConnectionBtn) {
        blockConnectionBtn.onclick = function() {
            showToast(`Blocking connection to ${alert.device.ip}...`, 'info');
            setTimeout(() => {
                showToast('Connection blocked successfully', 'success');
            }, 1500);
        };
    }
    
    // Quarantine device button
    const quarantineDeviceBtn = document.getElementById('quarantineDeviceBtn');
    if (quarantineDeviceBtn) {
        quarantineDeviceBtn.onclick = function() {
            showToast(`Quarantining device ${alert.device.name}...`, 'info');
            setTimeout(() => {
                showToast('Device quarantined successfully', 'success');
            }, 1500);
        };
    }
    
    // Resolve alert button
    const resolveAlertBtn = document.getElementById('resolveAlertBtn');
    if (resolveAlertBtn) {
        resolveAlertBtn.onclick = function() {
            showToast('Resolving alert...', 'info');
            
            // Simulate API call
            setTimeout(() => {
                showToast('Alert resolved successfully', 'success');
                
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('alertDetailModal'));
                if (modal) modal.hide();
                
                // Reload alerts
                loadAlerts();
            }, 1500);
        };
    }
}

/**
 * Get severity class for badge
 */
function getSeverityClass(severity) {
    switch(severity.toLowerCase()) {
        case 'critical': return 'danger';
        case 'high': return 'warning';
        case 'medium': return 'info';
        default: return 'secondary';
    }
}

/**
 * Set up filter controls
 */
function setupFilterControls() {
    const applyFiltersBtn = document.getElementById('applyFiltersBtn');
    
    if (applyFiltersBtn) {
        applyFiltersBtn.addEventListener('click', function() {
            // Get filter values
            const criticalChecked = document.getElementById('criticalFilter')?.checked || false;
            const highChecked = document.getElementById('highFilter')?.checked || false;
            const mediumChecked = document.getElementById('mediumFilter')?.checked || false;
            const lowChecked = document.getElementById('lowFilter')?.checked || false;
            
            const statusFilter = document.getElementById('statusFilter')?.value || 'all';
            
            // For demo, just show toast
            showToast('Filters applied', 'info');
            
            // In a real implementation, you would filter the table based on these values
            const rows = document.querySelectorAll('#alertsTableBody tr');
            
            rows.forEach(row => {
                const alertId = row.getAttribute('data-alert-id');
                if (!alertId) return;
                
                // This is where you would apply the actual filtering logic
            });
        });
    }
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    // Check if toast container exists, if not create it
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toastId = 'toast-' + Date.now();
    const toastElement = document.createElement('div');
    toastElement.className = `toast align-items-center border-0 bg-${type}`;
    toastElement.id = toastId;
    toastElement.setAttribute('role', 'alert');
    toastElement.setAttribute('aria-live', 'assertive');
    toastElement.setAttribute('aria-atomic', 'true');
    
    // Toast content
    toastElement.innerHTML = `
        <div class="d-flex">
            <div class="toast-body text-white">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    // Add toast to container
    toastContainer.appendChild(toastElement);
    
    // Initialize and show toast
    if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
        const toast = new bootstrap.Toast(toastElement, {
            autohide: true,
            delay: 3000
        });
        toast.show();
    }
    
    // Remove toast after it's hidden
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}
