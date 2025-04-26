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
});

/**
 * Initialize sidebar functionality
 */
function initSidebar() {
    const sidebarCollapse = document.getElementById('sidebarCollapse');
    const sidebar = document.getElementById('sidebar');
    const content = document.getElementById('content');
    
    if (sidebarCollapse && sidebar && content) {
        // Check saved state
        const isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
        
        // Apply saved state
        sidebar.classList.toggle('collapsed', isCollapsed);
        content.classList.toggle('expanded', isCollapsed);
        
        // Add click handler
        sidebarCollapse.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            content.classList.toggle('expanded');
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
        // Check for saved preference
        const isDarkMode = localStorage.getItem('theme') === 'dark' || 
            (!localStorage.getItem('theme') && window.matchMedia('(prefers-color-scheme: dark)').matches);
        
        // Set initial state
        darkModeToggle.checked = isDarkMode;
        document.body.classList.toggle('dark-theme', isDarkMode);
        document.documentElement.setAttribute('data-bs-theme', isDarkMode ? 'dark' : 'light');
        
        // Add change event
        darkModeToggle.addEventListener('change', function() {
            const isDark = this.checked;
            document.body.classList.toggle('dark-theme', isDark);
            document.documentElement.setAttribute('data-bs-theme', isDark ? 'dark' : 'light');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
            
            // Update radio buttons on settings page if they exist
            const lightModeRadio = document.getElementById('lightMode');
            const darkModeRadio = document.getElementById('darkMode');
            const systemModeRadio = document.getElementById('systemMode');
            
            if (lightModeRadio && darkModeRadio && systemModeRadio) {
                if (isDark) {
                    darkModeRadio.checked = true;
                } else {
                    lightModeRadio.checked = true;
                }
            }
        });
    }
}

/**
 * Initialize accent color
 */
function initAccentColor() {
    // Check if we have accent color options (only on settings page)
    const colorOptions = document.querySelectorAll('.color-option');
    
    // Get saved accent color
    const savedAccentColor = localStorage.getItem('accentColor') || '#2c7be5'; // Default blue
    
    // Apply the saved accent color
    applyAccentColor(savedAccentColor);
    
    // If we're on the settings page with color options
    if (colorOptions.length > 0) {
        // Set active color option
        colorOptions.forEach(option => {
            const bgColor = getComputedStyle(option).backgroundColor;
            const hexColor = rgbToHex(bgColor);
            
            // Mark the active option
            if (hexColor.toLowerCase() === savedAccentColor.toLowerCase()) {
                option.style.border = '2px solid var(--color-text-primary)';
            }
            
            // Add click handler
            option.addEventListener('click', function() {
                // Reset all borders
                colorOptions.forEach(opt => opt.style.border = '2px solid transparent');
                
                // Set active border
                this.style.border = '2px solid var(--color-text-primary)';
                
                // Get selected color
                const bgColor = getComputedStyle(this).backgroundColor;
                const hexColor = rgbToHex(bgColor);
                
                // Save and apply the accent color
                localStorage.setItem('accentColor', hexColor);
                applyAccentColor(hexColor);
                
                // Show a notification
                showToast('Accent color updated', 'success');
            });
        });
    }
}

/**
 * Apply accent color to the site
 * @param {string} color - Hex color code (optional, will use saved color if not provided)
 */
function applyAccentColor(color) {
    const accentColor = color || localStorage.getItem('accentColor') || '#2c7be5'; // Default blue
    
    // Create or update CSS variables for primary color
    document.documentElement.style.setProperty('--color-primary', accentColor);
    
    // Extract RGB values for the CSS variable
    const rgbValues = hexToRgb(accentColor);
    if (rgbValues) {
        document.documentElement.style.setProperty('--color-primary-rgb', `${rgbValues.r}, ${rgbValues.g}, ${rgbValues.b}`);
    }
    
    // Update any elements that use the accent color directly
    const accentElements = document.querySelectorAll('.accent-color');
    accentElements.forEach(el => {
        el.style.color = accentColor;
    });
    
    const accentBgElements = document.querySelectorAll('.accent-bg');
    accentBgElements.forEach(el => {
        el.style.backgroundColor = accentColor;
    });
}

/**
 * Convert RGB color to Hex
 * @param {string} rgb - RGB color string like "rgb(44, 123, 229)"
 * @return {string} Hex color code like "#2c7be5"
 */
function rgbToHex(rgb) {
    // Check if the input is already a hex color
    if (rgb.startsWith('#')) {
        return rgb;
    }
    
    // Extract RGB values
    const matches = rgb.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);
    if (!matches) {
        return '#2c7be5'; // Default blue if parsing fails
    }
    
    // Convert to hex
    function componentToHex(c) {
        const hex = parseInt(c).toString(16);
        return hex.length === 1 ? '0' + hex : hex;
    }
    
    return '#' + 
        componentToHex(matches[1]) + 
        componentToHex(matches[2]) + 
        componentToHex(matches[3]);
}

/**
 * Convert Hex color to RGB object
 * @param {string} hex - Hex color code like "#2c7be5"
 * @return {object|null} Object with r, g, b values or null if invalid
 */
function hexToRgb(hex) {
    // Expand shorthand form (e.g. "03F") to full form (e.g. "0033FF")
    const shorthandRegex = /^#?([a-f\d])([a-f\d])([a-f\d])$/i;
    hex = hex.replace(shorthandRegex, function(m, r, g, b) {
        return r + r + g + g + b + b;
    });

    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
    } : null;
}

/**
 * Load notifications into the dropdown
 */
function loadNotifications() {
    const container = document.getElementById('notificationsContainer');
    
    if (!container) return;
    
    // Example notifications
    const notifications = [
        {
            id: 'note1',
            type: 'alert',
            severity: 'critical',
            message: 'Critical vulnerability detected on Camera (192.168.1.101)',
            timestamp: Date.now() - 5 * 60 * 1000 // 5 minutes ago
        },
        {
            id: 'note2',
            type: 'info',
            severity: 'info',
            message: 'Scan completed for network 192.168.1.0/24',
            timestamp: Date.now() - 60 * 60 * 1000 // 1 hour ago
        },
        {
            id: 'note3',
            type: 'warning',
            severity: 'warning',
            message: 'Router firmware is out of date',
            timestamp: Date.now() - 3 * 60 * 60 * 1000 // 3 hours ago
        }
    ];
    
    // Clear container
    container.innerHTML = '';
    
    // Add notifications
    notifications.forEach(notification => {
        const notificationItem = document.createElement('li');
        notificationItem.classList.add('notification-item');
        
        if (notification.severity === 'critical') {
            notificationItem.classList.add('critical');
        }
        
        // Determine icon class
        let iconClass = 'bi-info-circle-fill';
        if (notification.type === 'alert') iconClass = 'bi-exclamation-triangle-fill';
        if (notification.type === 'warning') iconClass = 'bi-exclamation-circle-fill';
        
        // Format time ago
        const timeAgo = formatTimeAgo(notification.timestamp);
        
        notificationItem.innerHTML = `
            <div class="notification-icon">
                <i class="bi ${iconClass}"></i>
            </div>
            <div class="notification-content">
                <div class="notification-message">${notification.message}</div>
                <div class="notification-time">${timeAgo}</div>
            </div>
        `;
        
        container.appendChild(notificationItem);
    });
}

/**
 * Format timestamp as time ago
 */
function formatTimeAgo(timestamp) {
    const now = Date.now();
    const seconds = Math.floor((now - timestamp) / 1000);
    
    if (seconds < 60) return 'Just now';
    
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes} minute${minutes !== 1 ? 's' : ''} ago`;
    
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours} hour${hours !== 1 ? 's' : ''} ago`;
    
    const days = Math.floor(hours / 24);
    return `${days} day${days !== 1 ? 's' : ''} ago`;
}

/**
 * Show a toast notification
 */
function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toastId = 'toast-' + Date.now();
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'primary'} border-0`;
    toast.id = toastId;
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
    
    // Add toast to container
    toastContainer.appendChild(toast);
    
    // Show the toast
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove from DOM after hidden
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}
