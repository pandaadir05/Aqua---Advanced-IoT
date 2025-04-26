/**
 * Aqua IoT Security Platform
 * Live Activity Page Functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize charts and graphs
    initNetworkTrafficChart();
    initProtocolChart();
    initTopTalkersChart();
    
    // Set up event listeners
    setupRefreshButton();
    setupAutoRefreshToggle();
    setupRangeSelector();
    setupClearLogButton();
    
    // Initial data load
    loadConnectionData();
    loadDeviceStatusData();
    populateEventLog();
    
    // Set up auto refresh if enabled
    if (document.getElementById('autoRefreshToggle').checked) {
        startAutoRefresh();
    }
});

/**
 * Initialize the network traffic chart
 */
function initNetworkTrafficChart() {
    const chartElement = document.getElementById('networkTrafficChart');
    
    if (!chartElement) return;
    
    // Generate time points for the last hour
    const timePoints = [];
    const trafficData = [];
    const packetLossData = [];
    
    // Get current time and generate data points for the past hour
    const now = new Date();
    for (let i = 60; i >= 0; i--) {
        const time = new Date(now);
        time.setMinutes(now.getMinutes() - i);
        timePoints.push(time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }));
        
        // Generate random data for demonstration
        trafficData.push(Math.floor(Math.random() * 100) + 20);
        packetLossData.push(Math.floor(Math.random() * 5));
    }
    
    const options = {
        series: [
            {
                name: 'Network Traffic (Mbps)',
                data: trafficData
            },
            {
                name: 'Packet Loss (%)',
                data: packetLossData
            }
        ],
        chart: {
            height: 300,
            type: 'line',
            toolbar: {
                show: false
            },
            animations: {
                enabled: true,
                easing: 'linear',
                dynamicAnimation: {
                    speed: 1000
                }
            }
        },
        stroke: {
            curve: 'smooth',
            width: [3, 2]
        },
        colors: ['#2c7be5', '#e63757'],
        dataLabels: {
            enabled: false
        },
        markers: {
            size: 0
        },
        xaxis: {
            categories: timePoints
        },
        yaxis: [
            {
                title: {
                    text: 'Network Traffic (Mbps)'
                }
            },
            {
                opposite: true,
                title: {
                    text: 'Packet Loss (%)'
                },
                min: 0,
                max: 10
            }
        ],
        legend: {
            position: 'top'
        },
        grid: {
            borderColor: '#e0e0e0'
        }
    };
    
    const chart = new ApexCharts(chartElement, options);
    chart.render();
    
    // Store chart reference for updates
    window.networkTrafficChart = chart;
}

/**
 * Initialize the protocol distribution chart
 */
function initProtocolChart() {
    const chartElement = document.getElementById('protocolChart');
    
    if (!chartElement) return;
    
    const options = {
        series: [30, 25, 15, 10, 8, 12],
        chart: {
            type: 'pie',
            height: 300,
            toolbar: {
                show: false
            }
        },
        labels: ['HTTP/HTTPS', 'MQTT', 'DNS', 'SSH', 'RTSP', 'Other'],
        colors: ['#2c7be5', '#00b274', '#f6c343', '#e63757', '#6b5eae', '#95aac9'],
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
    
    const chart = new ApexCharts(chartElement, options);
    chart.render();
}

/**
 * Initialize the top talkers chart
 */
function initTopTalkersChart() {
    const chartElement = document.getElementById('topTalkersChart');
    
    if (!chartElement) return;
    
    const options = {
        series: [{
            name: 'Traffic (MB)',
            data: [350, 275, 240, 210, 190, 165, 140, 120, 95, 80]
        }],
        chart: {
            type: 'bar',
            height: 300,
            toolbar: {
                show: false
            }
        },
        plotOptions: {
            bar: {
                horizontal: true,
                barHeight: '70%'
            }
        },
        dataLabels: {
            enabled: false
        },
        xaxis: {
            categories: [
                '192.168.1.101', '192.168.1.105', '192.168.1.104', '192.168.1.102', 
                '192.168.1.110', '192.168.1.103', '192.168.1.108', '192.168.1.107',
                '192.168.1.106', '192.168.1.112'
            ]
        },
        colors: ['#2c7be5'],
        tooltip: {
            y: {
                formatter: function(value) {
                    return value + ' MB';
                }
            }
        }
    };
    
    const chart = new ApexCharts(chartElement, options);
    chart.render();
}

/**
 * Setup refresh button
 */
function setupRefreshButton() {
    const refreshButton = document.getElementById('refreshButton');
    
    if (refreshButton) {
        refreshButton.addEventListener('click', function() {
            refreshData();
        });
    }
}

/**
 * Setup auto-refresh toggle
 */
function setupAutoRefreshToggle() {
    const autoRefreshToggle = document.getElementById('autoRefreshToggle');
    
    if (autoRefreshToggle) {
        autoRefreshToggle.addEventListener('change', function() {
            if (this.checked) {
                startAutoRefresh();
            } else {
                stopAutoRefresh();
            }
        });
    }
}

/**
 * Start auto-refresh
 */
function startAutoRefresh() {
    if (!window.refreshInterval) {
        window.refreshInterval = setInterval(refreshData, 10000); // Refresh every 10 seconds
    }
}

/**
 * Stop auto-refresh
 */
function stopAutoRefresh() {
    if (window.refreshInterval) {
        clearInterval(window.refreshInterval);
        window.refreshInterval = null;
    }
}

/**
 * Refresh all data
 */
function refreshData() {
    updateNetworkTrafficChart();
    loadConnectionData();
    loadDeviceStatusData();
    addRandomEventToLog();
}

/**
 * Update the network traffic chart with new data
 */
function updateNetworkTrafficChart() {
    if (window.networkTrafficChart) {
        const chart = window.networkTrafficChart;
        
        // Get current series data
        let trafficData = chart.w.globals.series[0].slice();
        let packetLossData = chart.w.globals.series[1].slice();
        
        // Remove first data point
        trafficData.shift();
        packetLossData.shift();
        
        // Add new random data point
        trafficData.push(Math.floor(Math.random() * 100) + 20);
        packetLossData.push(Math.floor(Math.random() * 5));
        
        // Update chart
        chart.updateSeries([
            { data: trafficData },
            { data: packetLossData }
        ]);
    }
}

/**
 * Load connection data
 */
function loadConnectionData() {
    const connectionsTable = document.getElementById('connectionsTable');
    const connectionsCount = document.getElementById('connectionsCount');
    
    if (!connectionsTable) return;
    
    // Clear existing content
    connectionsTable.innerHTML = '';
    
    // Demo connection data
    const connections = [
        { source: '192.168.1.101', destination: '192.168.1.1', protocol: 'TCP', state: 'ESTABLISHED' },
        { source: '192.168.1.105', destination: '8.8.8.8', protocol: 'UDP', state: 'ESTABLISHED' },
        { source: '192.168.1.104', destination: '192.168.1.1', protocol: 'TCP', state: 'ESTABLISHED' },
        { source: '192.168.1.102', destination: '192.168.1.103', protocol: 'TCP', state: 'ESTABLISHED' },
        { source: '192.168.1.101', destination: '192.168.1.106', protocol: 'MQTT', state: 'ESTABLISHED' },
        { source: '192.168.1.110', destination: '192.168.1.1', protocol: 'TCP', state: 'TIME_WAIT' },
        { source: '192.168.1.107', destination: '172.217.169.174', protocol: 'TCP', state: 'ESTABLISHED' },
        { source: '192.168.1.108', destination: '192.168.1.1', protocol: 'UDP', state: 'ESTABLISHED' },
        { source: '192.168.1.112', destination: '192.168.1.115', protocol: 'TCP', state: 'ESTABLISHED' }
    ];
    
    // Update the connections count
    if (connectionsCount) {
        connectionsCount.textContent = connections.length;
    }
    
    // Add connections to table
    connections.forEach(conn => {
        const row = document.createElement('tr');
        
        row.innerHTML = `
            <td>${conn.source}</td>
            <td>${conn.destination}</td>
            <td>${conn.protocol}</td>
            <td>${conn.state}</td>
        `;
        
        connectionsTable.appendChild(row);
    });
}

/**
 * Load device status data
 */
function loadDeviceStatusData() {
    const deviceStatusList = document.getElementById('deviceStatusList');
    
    if (!deviceStatusList) return;
    
    // Clear existing content
    deviceStatusList.innerHTML = '';
    
    // Demo device status data
    const devices = [
        { id: 'dev001', name: 'Security Camera', ip: '192.168.1.101', status: 'online', cpu: 45, memory: 62 },
        { id: 'dev002', name: 'Smart Speaker', ip: '192.168.1.102', status: 'online', cpu: 12, memory: 34 },
        { id: 'dev003', name: 'Router', ip: '192.168.1.1', status: 'online', cpu: 78, memory: 58 },
        { id: 'dev004', name: 'Thermostat', ip: '192.168.1.103', status: 'online', cpu: 8, memory: 22 },
        { id: 'dev005', name: 'Smart Lock', ip: '192.168.1.104', status: 'offline', cpu: 0, memory: 0 }
    ];
    
    // Add devices to list
    devices.forEach(device => {
        const item = document.createElement('div');
        item.className = 'list-group-item';
        
        // Determine status class
        const statusClass = device.status === 'online' ? 'bg-success' : 'bg-secondary';
        
        item.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h6 class="mb-0">${device.name}</h6>
                    <small class="text-muted">${device.ip}</small>
                </div>
                <span class="badge ${statusClass}">${device.status}</span>
            </div>
            ${device.status === 'online' ? `
                <div class="mt-2">
                    <div class="d-flex justify-content-between small mb-1">
                        <span>CPU</span>
                        <span>${device.cpu}%</span>
                    </div>
                    <div class="progress" style="height: 5px;">
                        <div class="progress-bar bg-primary" role="progressbar" style="width: ${device.cpu}%" aria-valuenow="${device.cpu}" aria-valuemin="0" aria-valuemax="100"></div>
                    </div>
                </div>
                <div class="mt-2">
                    <div class="d-flex justify-content-between small mb-1">
                        <span>Memory</span>
                        <span>${device.memory}%</span>
                    </div>
                    <div class="progress" style="height: 5px;">
                        <div class="progress-bar bg-warning" role="progressbar" style="width: ${device.memory}%" aria-valuenow="${device.memory}" aria-valuemin="0" aria-valuemax="100"></div>
                    </div>
                </div>
            ` : ''}
        `;
        
        deviceStatusList.appendChild(item);
    });
}

/**
 * Setup range selector for time range options
 */
function setupRangeSelector() {
    const rangeOptions = document.querySelectorAll('.time-range-option');
    
    rangeOptions.forEach(option => {
        option.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all options
            rangeOptions.forEach(opt => opt.classList.remove('active'));
            
            // Add active class to selected option
            this.classList.add('active');
            
            // Get selected range in minutes
            const range = parseInt(this.getAttribute('data-range'));
            
            // Update time range of data (in a real app this would refresh the charts and data)
            console.log(`Selected time range: ${range} minutes`);
        });
    });
}

/**
 * Setup clear log button
 */
function setupClearLogButton() {
    const clearLogBtn = document.getElementById('clearLogBtn');
    const eventLog = document.getElementById('eventLog');
    
    if (clearLogBtn && eventLog) {
        clearLogBtn.addEventListener('click', function() {
            eventLog.innerHTML = '';
        });
    }
}

/**
 * Populate event log with initial events
 */
function populateEventLog() {
    const eventLog = document.getElementById('eventLog');
    
    if (!eventLog) return;
    
    // Clear existing content
    eventLog.innerHTML = '';
    
    // Add some initial events
    const events = [
        { timestamp: '11:42:15', type: 'warning', message: 'Unusual traffic detected from 192.168.1.101', details: 'Excessive outbound connections' },
        { timestamp: '11:38:02', type: 'info', message: 'Device 192.168.1.105 connected to the network', details: 'MAC: AA:BB:CC:DD:EE:FF' },
        { timestamp: '11:35:47', type: 'error', message: 'Authentication failure on device 192.168.1.104', details: 'Multiple failed login attempts' },
        { timestamp: '11:30:21', type: 'info', message: 'Scan completed on network 192.168.1.0/24', details: '15 devices discovered' },
        { timestamp: '11:28:05', type: 'warning', message: 'Outdated firmware detected on 192.168.1.103', details: 'Current version: 2.1.4, Latest: 3.0.1' }
    ];
    
    // Add events to log
    events.forEach(event => {
        addEventToLog(event);
    });
}

/**
 * Add an event to the log
 */
function addEventToLog(event) {
    const eventLog = document.getElementById('eventLog');
    
    if (!eventLog) return;
    
    const eventElement = document.createElement('div');
    eventElement.className = `event-item event-${event.type}`;
    
    // Format timestamp or use the provided one
    const timestamp = event.timestamp || new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    
    // Determine icon based on event type
    let iconClass;
    switch(event.type) {
        case 'error':
            iconClass = 'bi-exclamation-octagon-fill';
            break;
        case 'warning':
            iconClass = 'bi-exclamation-triangle-fill';
            break;
        case 'info':
        default:
            iconClass = 'bi-info-circle-fill';
            break;
    }
    
    eventElement.innerHTML = `
        <div class="event-time">${timestamp}</div>
        <div class="event-icon"><i class="bi ${iconClass}"></i></div>
        <div class="event-content">
            <div class="event-message">${event.message}</div>
            <div class="event-details text-muted small">${event.details || ''}</div>
        </div>
    `;
    
    // Add to the beginning of the log
    eventLog.insertBefore(eventElement, eventLog.firstChild);
    
    // If auto-scroll is enabled, scroll to the top
    const autoscrollToggle = document.getElementById('autoscrollToggle');
    if (autoscrollToggle && autoscrollToggle.checked) {
        eventLog.scrollTop = 0;
    }
}

/**
 * Add a random event to the log (for simulation)
 */
function addRandomEventToLog() {
    const eventTypes = ['info', 'warning', 'error'];
    const eventMessages = [
        { type: 'info', message: 'Device connected to the network', details: 'IP: 192.168.1.[X], MAC: AA:BB:CC:[X]:EE:FF' },
        { type: 'info', message: 'Network traffic normal', details: 'Average: [X] Mbps' },
        { type: 'warning', message: 'High CPU usage detected', details: 'Device: 192.168.1.[X], CPU: [Y]%' },
        { type: 'warning', message: 'Unusual port scan detected', details: 'Source: 192.168.1.[X], Ports: [Y]-[Z]' },
        { type: 'error', message: 'Connection attempt blocked', details: 'Source: 192.168.1.[X], Destination: [Y].[Y].[Y].[Y]' },
        { type: 'error', message: 'Authentication failure', details: 'Device: 192.168.1.[X], User: admin' }
    ];
    
    // Select a random event type
    const eventType = eventTypes[Math.floor(Math.random() * eventTypes.length)];
    
    // Filter messages by type
    const typeMessages = eventMessages.filter(e => e.type === eventType);
    
    // Select a random message
    const eventTemplate = typeMessages[Math.floor(Math.random() * typeMessages.length)];
    
    // Replace placeholders with random values
    let message = eventTemplate.message;
    let details = eventTemplate.details;
    
    details = details.replace('[X]', Math.floor(Math.random() * 254) + 1);
    details = details.replace('[Y]', Math.floor(Math.random() * 100));
    details = details.replace('[Z]', Math.floor(Math.random() * 1000) + 100);
    
    // Add the event to log
    addEventToLog({
        type: eventType,
        message: message,
        details: details
    });
}
