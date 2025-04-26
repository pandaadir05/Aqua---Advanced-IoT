/**
 * Aqua IoT Security Platform
 * Vulnerabilities Page Functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Load vulnerability data
    loadVulnerabilities();
    
    // Initialize vulnerability chart
    initVulnerabilityTrendsChart();
    
    // Set up event listeners
    setupVulnerabilityFilters();
    setupVulnerabilitySearch();
    setupVulnerabilityDetailHandlers();
});

/**
 * Load vulnerabilities from API
 */
function loadVulnerabilities() {
    // Show loading state
    document.getElementById('vulnerabilitiesTable').innerHTML = `
        <tr>
            <td colspan="9" class="text-center py-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">Loading vulnerabilities...</p>
            </td>
        </tr>
    `;
    
    // Fetch vulnerabilities from API
    fetch('/api/vulnerabilities')
        .then(response => response.json())
        .then(vulnerabilities => {
            // Update stats
            updateVulnerabilityStats(vulnerabilities);
            
            // Populate table
            populateVulnerabilityTable(vulnerabilities);
        })
        .catch(error => {
            console.error('Error loading vulnerabilities:', error);
            document.getElementById('vulnerabilitiesTable').innerHTML = `
                <tr>
                    <td colspan="9" class="text-center py-4">
                        <div class="alert alert-danger">
                            Failed to load vulnerabilities. Please try again.
                        </div>
                    </td>
                </tr>
            `;
        });
}

/**
 * Update vulnerability stats based on loaded data
 */
function updateVulnerabilityStats(vulnerabilities) {
    // Count by severity
    const criticalCount = vulnerabilities.filter(v => v.severity === 'Critical').length;
    const highCount = vulnerabilities.filter(v => v.severity === 'High').length;
    const mediumCount = vulnerabilities.filter(v => v.severity === 'Medium').length;
    const lowCount = vulnerabilities.filter(v => v.severity === 'Low').length;
    
    // Update stats cards
    document.getElementById('criticalVulnCount').textContent = criticalCount;
    document.getElementById('highVulnCount').textContent = highCount;
    document.getElementById('mediumVulnCount').textContent = mediumCount;
    document.getElementById('lowVulnCount').textContent = lowCount;
}

/**
 * Populate vulnerability table with data
 */
function populateVulnerabilityTable(vulnerabilities) {
    const tableBody = document.getElementById('vulnerabilitiesTable');
    
    // Clear table body
    tableBody.innerHTML = '';
    
    // Check if we have vulnerabilities
    if (vulnerabilities.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="9" class="text-center py-4">
                    <div class="alert alert-info">
                        No vulnerabilities found. Your network is secure!
                    </div>
                </td>
            </tr>
        `;
        return;
    }
    
    // Add rows for each vulnerability
    vulnerabilities.forEach(vuln => {
        fetch(`/api/devices/${vuln.device_id}`)
            .then(response => response.json())
            .then(device => {
                const row = document.createElement('tr');
                row.setAttribute('data-vulnerability-id', vuln.id);
                
                // Determine severity class
                let severityClass = '';
                switch(vuln.severity) {
                    case 'Critical': severityClass = 'badge-critical'; break;
                    case 'High': severityClass = 'badge-high'; break;
                    case 'Medium': severityClass = 'badge-medium'; break;
                    default: severityClass = 'badge-low';
                }
                
                // Calculate "age" - for the demo we'll use random values
                const age = 'Today';
                
                row.innerHTML = `
                    <td>
                        <div class="form-check">
                            <input class="form-check-input vulnerability-checkbox" type="checkbox" value="${vuln.id}">
                        </div>
                    </td>
                    <td>
                        <div class="fw-medium">${vuln.name}</div>
                        <div class="small text-muted">${vuln.details}</div>
                    </td>
                    <td><span class="badge ${severityClass}">${vuln.severity}</span></td>
                    <td>CVE-2023-1234</td>
                    <td>
                        <div class="fw-medium">${device.ip}</div>
                        <div class="small text-muted">${device.type}</div>
                    </td>
                    <td>7.5</td>
                    <td><span class="badge bg-warning text-dark">Open</span></td>
                    <td>${age}</td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary view-vulnerability-btn" data-vuln-id="${vuln.id}">
                            View
                        </button>
                    </td>
                `;
                
                tableBody.appendChild(row);
            })
            .catch(error => {
                console.error('Error loading device info for vulnerability:', error);
            });
    });
}

/**
 * Initialize vulnerability trends chart
 */
function initVulnerabilityTrendsChart() {
    const chartElement = document.getElementById('vulnerabilityTrendsChart');
    
    if (!chartElement) return;
    
    // Generate dates for the past week
    const dates = [];
    for (let i = 6; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        dates.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
    }
    
    // Demo data
    const criticalData = [2, 3, 3, 4, 2, 3, 2];
    const highData = [5, 4, 6, 5, 7, 6, 5];
    const mediumData = [8, 9, 7, 8, 6, 7, 9];
    const lowData = [4, 5, 3, 2, 5, 4, 3];
    
    const options = {
        series: [
            {
                name: 'Critical',
                data: criticalData
            },
            {
                name: 'High',
                data: highData
            },
            {
                name: 'Medium',
                data: mediumData
            },
            {
                name: 'Low',
                data: lowData
            }
        ],
        chart: {
            type: 'area',
            height: 300,
            toolbar: {
                show: false
            },
            animations: {
                enabled: true
            }
        },
        colors: ['#e63757', '#fd7e14', '#f6c343', '#39afd1'],
        dataLabels: {
            enabled: false
        },
        stroke: {
            curve: 'smooth',
            width: 2
        },
        fill: {
            type: 'gradient',
            gradient: {
                opacityFrom: 0.6,
                opacityTo: 0.1
            }
        },
        legend: {
            position: 'top',
            horizontalAlign: 'right'
        },
        xaxis: {
            categories: dates
        },
        tooltip: {
            x: {
                format: 'dd MMM'
            }
        }
    };
    
    const chart = new ApexCharts(chartElement, options);
    chart.render();
}

/**
 * Set up vulnerability filters
 */
function setupVulnerabilityFilters() {
    // Add filter change handlers
    const filters = document.querySelectorAll('#severityFilter, #deviceTypeVulnFilter, #statusVulnFilter, #ageFilter');
    filters.forEach(filter => {
        filter.addEventListener('change', function() {
            // This would filter the vulnerability table based on selected values
            console.log('Filter applied:', this.id, this.value);
            // In a real implementation, this would re-fetch or filter the vulnerability list
        });
    });
}

/**
 * Set up vulnerability search
 */
function setupVulnerabilitySearch() {
    const searchInput = document.getElementById('vulnSearch');
    const searchButton = document.getElementById('searchVulnBtn');
    
    if (searchButton && searchInput) {
        searchButton.addEventListener('click', function() {
            const searchTerm = searchInput.value.toLowerCase();
            const rows = document.querySelectorAll('#vulnerabilitiesTable tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            });
        });
    }
}

/**
 * Set up vulnerability detail modal handlers
 */
function setupVulnerabilityDetailHandlers() {
    // Delegation for view buttons
    document.addEventListener('click', function(e) {
        if (e.target && e.target.classList.contains('view-vulnerability-btn')) {
            const vulnerabilityId = e.target.getAttribute('data-vuln-id');
            openVulnerabilityDetailModal(vulnerabilityId);
        }
    });
    
    // Save button handler
    const saveVulnBtn = document.getElementById('saveVulnBtn');
    if (saveVulnBtn) {
        saveVulnBtn.addEventListener('click', function() {
            // In a real app, this would save changes to the vulnerability
            const modal = bootstrap.Modal.getInstance(document.getElementById('vulnerabilityDetailModal'));
            modal.hide();
            
            showToast('Vulnerability updated successfully', 'success');
        });
    }
}

/**
 * Open vulnerability detail modal with data
 */
function openVulnerabilityDetailModal(vulnerabilityId) {
    // In a real app, fetch the vulnerability details from the API
    // For demo, we'll use placeholder data
    
    // Populate modal fields
    document.getElementById('vulnDetailName').textContent = 'Default Credentials';
    document.getElementById('vulnDetailSeverity').textContent = 'Critical';
    document.getElementById('vulnDetailCvss').textContent = '9.1';
    document.getElementById('vulnDetailCve').textContent = 'CVE-2023-1234';
    document.getElementById('vulnDetailDevice').textContent = '192.168.1.101 (Camera)';
    document.getElementById('vulnDetailDate').textContent = 'Oct 28, 2023';
    document.getElementById('vulnDetailStatus').value = 'Open';
    document.getElementById('vulnDetailDescription').textContent = 'Device is using default manufacturer credentials which are widely known and documented.';
    document.getElementById('vulnDetailRemediation').textContent = 'Change the default credentials to strong, unique passwords. Implement a regular password rotation policy.';
    
    // References
    const referencesEl = document.getElementById('vulnDetailReferences');
    referencesEl.innerHTML = `
        <li><a href="https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2023-1234" target="_blank">CVE-2023-1234</a></li>
        <li><a href="https://nvd.nist.gov/vuln/detail/CVE-2023-1234" target="_blank">NVD Reference</a></li>
    `;
    
    // Show the modal
    const modal = new bootstrap.Modal(document.getElementById('vulnerabilityDetailModal'));
    modal.show();
}
