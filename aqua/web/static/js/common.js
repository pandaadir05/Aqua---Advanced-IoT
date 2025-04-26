/**
 * Aqua IoT Security Platform
 * Common JavaScript functionality used across all pages
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the sidebar
    initSidebar();
    
    // Initialize the dark mode toggle
    initDarkModeToggle();
    
    // Initialize accent color if available
    initAccentColor();
    
    // Load notifications
    loadNotifications();
    
    // Set up global toast container
    setupToastContainer();
});

/**
 * Initialize sidebar functionality
 */
function initSidebar() {
    const sidebarToggle = document.getElementById('sidebarCollapse');
    const sidebar = document.getElementById('sidebar');
    
    if (sidebarToggle && sidebar) {
        // Check for saved state
        const sidebarCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
        
        if (sidebarCollapsed) {
            document.body.classList.add('sidebar-collapsed');
            sidebar.classList.add('collapsed');
        }
        
        sidebarToggle.addEventListener('click', function() {
            document.body.classList.toggle('sidebar-collapsed');
            sidebar.classList.toggle('collapsed');
            
            // Save state
            localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
        });
    }
}

/**
 * Initialize dark mode toggle
 */
function initDarkModeToggle() {
    const darkModeToggle = document.getElementById('darkModeToggle');
    
    if (darkModeToggle) {
        // Check for saved preference or system preference
        const savedTheme = localStorage.getItem('theme');
        const systemPrefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        // Default to system preference if no saved preference
        const isDarkMode = savedTheme ? savedTheme === 'dark' : systemPrefersDark;
        
        // Set initial state
        darkModeToggle.checked = isDarkMode;
        document.body.classList.toggle('dark-mode', isDarkMode);
        
        // Update meta theme-color
        updateThemeColor(isDarkMode);
        
        // Handle toggle
        darkModeToggle.addEventListener('change', function() {
            const isDark = this.checked;
            document.body.classList.toggle('dark-mode', isDark);
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
            updateThemeColor(isDark);
            
            // Update charts if they exist
            updateChartsTheme(isDark);
        });
    }
}

/**
 * Update theme color meta tag
 */
function updateThemeColor(isDarkMode) {
    const themeColor = isDarkMode ? '#121212' : '#ffffff';
    let metaThemeColor = document.querySelector('meta[name="theme-color"]');
    
    if (!metaThemeColor) {
        metaThemeColor = document.createElement('meta');
        metaThemeColor.setAttribute('name', 'theme-color');
        document.head.appendChild(metaThemeColor);
    }
    
    metaThemeColor.setAttribute('content', themeColor);
}

/**
 * Update charts theme if charts exist
 */
function updateChartsTheme(isDarkMode) {
    const theme = {
        mode: isDarkMode ? 'dark' : 'light',
        palette: 'palette1'
    };
    
    // Check if ApexCharts is available
    if (window.ApexCharts) {
        ApexCharts.theme = theme;
        
        // Update all charts
        document.querySelectorAll('.apexcharts-canvas').forEach(chartElement => {
            const chartInstance = window.ApexCharts.getChartByID(chartElement.id.split('_')[0]);
            if (chartInstance) {
                chartInstance.updateOptions({
                    theme: theme,
                    tooltip: {
                        theme: isDarkMode ? 'dark' : 'light'
                    }
                });
            }
        });
    }
}

/**
 * Initialize accent color
 */
function initAccentColor() {
    const colorPicker = document.getElementById('accentColorPicker');
    
    if (colorPicker) {
        // Load saved accent color
        const savedColor = localStorage.getItem('accentColor');
        if (savedColor) {
            applyAccentColor(savedColor);
            colorPicker.value = savedColor;
        }
        
        // Handle color change
        colorPicker.addEventListener('change', function() {
            const color = this.value;
            applyAccentColor(color);
            localStorage.setItem('accentColor', color);
        });
    }
}

/**
 * Apply accent color to the site
 * @param {string} color - Hex color code (optional, will use saved color if not provided)
 */
function applyAccentColor(color) {
    color = color || localStorage.getItem('accentColor') || '#2c7be5';
    
    // Create CSS variable overrides
    const colorStyle = document.createElement('style');
    colorStyle.id = 'accent-color-style';
    
    // Remove existing style if it exists
    const existingStyle = document.getElementById('accent-color-style');
    if (existingStyle) {
        existingStyle.remove();
    }
    
    // Create color variations
    const darkerColor = adjustBrightness(color, -20);
    const lighterColor = adjustBrightness(color, 20);
    const transparentColor = hexToRGBA(color, 0.1);
    
    colorStyle.textContent = `
        :root {
            --color-primary: ${color};
            --color-primary-dark: ${darkerColor};
            --color-primary-light: ${lighterColor};
            --color-primary-transparent: ${transparentColor};
        }
    `;
    
    document.head.appendChild(colorStyle);
    
    // If we have buttons with accent-bg class, update their background
    document.querySelectorAll('.accent-bg').forEach(el => {
        el.style.backgroundColor = color;
        el.style.borderColor = color;
    });
}

/**
 * Adjust color brightness
 * @param {string} hex - Hex color code
 * @param {number} percent - Percentage to adjust (-100 to 100)
 * @returns {string} Adjusted hex color
 */
function adjustBrightness(hex, percent) {
    hex = hex.replace('#', '');
    
    const r = parseInt(hex.substring(0, 2), 16);
    const g = parseInt(hex.substring(2, 4), 16);
    const b = parseInt(hex.substring(4, 6), 16);
    
    const adjustedR = Math.max(0, Math.min(255, Math.round(r * (1 + percent / 100))));
    const adjustedG = Math.max(0, Math.min(255, Math.round(g * (1 + percent / 100))));
    const adjustedB = Math.max(0, Math.min(255, Math.round(b * (1 + percent / 100))));
    
    return `#${(adjustedR.toString(16).padStart(2, '0'))}${adjustedG.toString(16).padStart(2, '0')}${adjustedB.toString(16).padStart(2, '0')}`;
}

/**
 * Convert hex color to rgba
 */
function hexToRGBA(hex, alpha = 1) {
    hex = hex.replace('#', '');
    
    const r = parseInt(hex.substring(0, 2), 16);
    const g = parseInt(hex.substring(2, 4), 16);
    const b = parseInt(hex.substring(4, 6), 16);
    
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

/**
 * Convert RGB color to Hex
 * @param {string} rgb - RGB color string like "rgb(44, 123, 229)"
 * @return {string} Hex color code like "#2c7be5"
 */
function rgbToHex(rgb) {
    if (!rgb) return null;
    
    const match = rgb.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);
    if (!match) return null;
    
    function hex(x) {
        return ("0" + parseInt(x).toString(16)).slice(-2);
    }
    
    return "#" + hex(match[1]) + hex(match[2]) + hex(match[3]);
}

/**
 * Load notifications into the dropdown
 */
function loadNotifications() {
    const container = document.getElementById('notificationsContainer');
    if (!container) return;
    
    // Clear existing notifications
    container.innerHTML = '';
    
    // Fetch notifications from API (or use sample data for now)
    const notifications = getSampleNotifications();
    
    if (notifications.length === 0) {
        container.innerHTML = '<div class="text-center p-3">No notifications</div>';
        return;
    }
    
    // Add notifications to dropdown
    notifications.forEach(notification => {
        const notificationItem = document.createElement('div');
        notificationItem.className = 'dropdown-item notification-item';
        
        // Determine notification icon based on type
        let iconClass = 'bi bi-info-circle';
        let iconColor = 'primary';
        
        switch(notification.type) {
            case 'warning':
                iconClass = 'bi bi-exclamation-triangle';
                iconColor = 'warning';
                break;
            case 'error':
                iconClass = 'bi bi-exclamation-octagon';
                iconColor = 'danger';
                break;
            case 'success':
                iconClass = 'bi bi-check-circle';
                iconColor = 'success';
                break;
        }
        
        notificationItem.innerHTML = `
            <div class="notification-icon text-${iconColor}">
                <i class="${iconClass}"></i>
            </div>
            <div class="notification-content">
                <div class="notification-title">${notification.title}</div>
                <div class="notification-text text-muted small">${notification.message}</div>
                <div class="notification-time text-muted x-small">${formatTimeAgo(notification.timestamp)}</div>
            </div>
        `;
        
        container.appendChild(notificationItem);
    });
    
    // Update notification badge
    const notificationBadge = document.querySelector('.notification-badge');
    if (notificationBadge) {
        const unreadCount = notifications.filter(n => !n.read).length;
        notificationBadge.textContent = unreadCount;
        notificationBadge.style.display = unreadCount > 0 ? 'block' : 'none';
    }
}

/**
 * Get sample notifications for demo
 */
function getSampleNotifications() {
    return [
        {
            id: 1,
            type: 'error',
            title: 'Critical Vulnerability Detected',
            message: 'Default credentials found on Smart Camera (192.168.1.101)',
            timestamp: new Date(Date.now() - 1000 * 60 * 5), // 5 minutes ago
            read: false
        },
        {
            id: 2,
            type: 'warning',
            title: 'Unusual Network Traffic',
            message: 'High volume of outbound traffic from Smart Thermostat',
            timestamp: new Date(Date.now() - 1000 * 60 * 30), // 30 minutes ago
            read: false
        },
        {
            id: 3,
            type: 'success',
            title: 'Scan Completed',
            message: 'Full network scan completed successfully',
            timestamp: new Date(Date.now() - 1000 * 60 * 60), // 1 hour ago
            read: true
        },
        {
            id: 4,
            type: 'info',
            title: 'New Device Detected',
            message: 'New IoT device connected to network: Smart Speaker',
            timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2), // 2 hours ago
            read: true
        }
    ];
}

/**
 * Format time ago string
 * @param {Date} date - The date to format
 * @return {string} Formatted time ago string
 */
function formatTimeAgo(date) {
    const now = new Date();
    const diffMs = now - date;
    const diffSecs = Math.floor(diffMs / 1000);
    const diffMins = Math.floor(diffSecs / 60);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffSecs < 60) {
        return 'Just now';
    } else if (diffMins < 60) {
        return `${diffMins} ${diffMins === 1 ? 'minute' : 'minutes'} ago`;
    } else if (diffHours < 24) {
        return `${diffHours} ${diffHours === 1 ? 'hour' : 'hours'} ago`;
    } else if (diffDays < 7) {
        return `${diffDays} ${diffDays === 1 ? 'day' : 'days'} ago`;
    } else {
        return date.toLocaleDateString();
    }
}

/**
 * Set up global toast container
 */
function setupToastContainer() {
    // Create toast container if it doesn't exist
    if (!document.getElementById('toastContainer')) {
        const toastContainer = document.createElement('div');
        toastContainer.id = 'toastContainer';
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
}

/**
 * Show a toast notification
 * @param {string} message - Toast message
 * @param {string} type - Toast type (success, error, warning, info)
 */
function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        setupToastContainer();
        toastContainer = document.getElementById('toastContainer');
    }
    
    // Create toast
    const toastId = 'toast-' + Date.now();
    const toast = document.createElement('div');
    toast.id = toastId;
    toast.className = `toast align-items-center border-0 bg-${getToastClass(type)}`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Show toast
    const bsToast = new bootstrap.Toast(toast, {
        autohide: true,
        delay: 5000
    });
    bsToast.show();
    
    // Remove toast from DOM after it's hidden
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

/**
 * Get the Bootstrap class for a toast type
 */
function getToastClass(type) {
    switch (type) {
        case 'success':
            return 'success text-white';
        case 'error':
            return 'danger text-white';
        case 'warning':
            return 'warning';
        default:
            return 'info text-white';
    }
}

/**
 * Add a new notification
 * @param {Object} notification - Notification object
 */
function addNotification(notification) {
    // TODO: Add to notification storage or API
    
    // Refresh notifications in dropdown
    loadNotifications();
    
    // Show toast for new notification
    showToast(notification.message, notification.type);
}
