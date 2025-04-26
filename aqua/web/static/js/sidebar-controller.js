/**
 * Aqua IoT Security Platform
 * Sidebar Controller - Handles sidebar state across all pages
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize sidebar controller
    initSidebarController();
    
    // If sidebar exists, activate the correct menu item based on current page
    if (document.getElementById('sidebar')) {
        activateCurrentNavItem();
    }
});

/**
 * Initialize sidebar controller
 */
function initSidebarController() {
    const sidebarCollapse = document.getElementById('sidebarCollapse');
    const sidebar = document.getElementById('sidebar');
    const content = document.getElementById('content');
    
    if (!sidebar || !content) return;
    
    // Check saved sidebar state
    const sidebarState = localStorage.getItem('sidebarCollapsed');
    
    // Apply saved state
    if (sidebarState === 'true') {
        sidebar.classList.add('collapsed');
        content.classList.add('expanded');
    } else {
        sidebar.classList.remove('collapsed');
        content.classList.remove('expanded');
    }
    
    // Add toggle functionality
    if (sidebarCollapse) {
        sidebarCollapse.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            content.classList.toggle('expanded');
            
            // Save state
            localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
        });
    }
}

/**
 * Activate the current navigation item based on URL
 */
function activateCurrentNavItem() {
    const currentPath = window.location.pathname;
    const navItems = document.querySelectorAll('#sidebar li');
    
    // Remove active class from all items
    navItems.forEach(item => item.classList.remove('active'));
    
    // Find the matching nav item based on path
    let matchingItem = null;
    
    if (currentPath === '/' || currentPath === '/dashboard') {
        matchingItem = document.querySelector('#sidebar li[data-page="dashboard"]');
    } else if (currentPath.includes('/devices')) {
        matchingItem = document.querySelector('#sidebar li[data-page="devices"]');
    } else if (currentPath.includes('/vulnerabilities')) {
        matchingItem = document.querySelector('#sidebar li[data-page="vulnerabilities"]');
    } else if (currentPath.includes('/reports')) {
        matchingItem = document.querySelector('#sidebar li[data-page="reports"]');
    } else if (currentPath.includes('/live-activity')) {
        matchingItem = document.querySelector('#sidebar li[data-page="live-activity"]');
    } else if (currentPath.includes('/alerts')) {
        matchingItem = document.querySelector('#sidebar li[data-page="alerts"]');
    } else if (currentPath.includes('/settings')) {
        matchingItem = document.querySelector('#sidebar li[data-page="settings"]');
    } else if (currentPath.includes('/help')) {
        matchingItem = document.querySelector('#sidebar li[data-page="help"]');
    }
    
    // Activate the matching item
    if (matchingItem) {
        matchingItem.classList.add('active');
    }
}
