/**
 * Aqua IoT Security Platform
 * Theme Controller - Handles dark/light theme switching
 */

document.addEventListener('DOMContentLoaded', function() {
    initThemeController();
});

/**
 * Initialize theme controller
 */
function initThemeController() {
    const darkModeToggle = document.getElementById('darkModeToggle');
    
    // Check system preference
    const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
    
    // Check stored preference
    const storedTheme = localStorage.getItem('theme');
    
    // Determine which theme to use
    let isDarkMode = false;
    
    if (storedTheme === 'dark') {
        isDarkMode = true;
    } else if (storedTheme === 'light') {
        isDarkMode = false;
    } else if (prefersDarkScheme.matches) {
        isDarkMode = true;
    }
    
    // Apply the theme
    applyTheme(isDarkMode);
    
    // Update the toggle switch if it exists
    if (darkModeToggle) {
        darkModeToggle.checked = isDarkMode;
        
        // Add direct click handler instead of change event
        darkModeToggle.addEventListener('click', function() {
            // Use the checked state after click
            const newDarkMode = this.checked;
            applyTheme(newDarkMode);
            localStorage.setItem('theme', newDarkMode ? 'dark' : 'light');
        });
    }
    
    // Listen for system preference changes
    prefersDarkScheme.addEventListener('change', function(e) {
        // Only adjust theme based on system if user hasn't set a preference
        if (!localStorage.getItem('theme')) {
            applyTheme(e.matches);
            if (darkModeToggle) {
                darkModeToggle.checked = e.matches;
            }
        }
    });
}

/**
 * Apply theme based on dark mode preference
 */
function applyTheme(isDark) {
    if (isDark) {
        document.body.classList.add('dark-theme');
        document.documentElement.setAttribute('data-bs-theme', 'dark');
    } else {
        document.body.classList.remove('dark-theme');
        document.documentElement.setAttribute('data-bs-theme', 'light');
    }
}
