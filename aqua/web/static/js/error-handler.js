/**
 * Aqua IoT Security Platform
 * Global Error Handler
 */

// Set up global error handling
window.addEventListener('error', function(event) {
    console.error('Global error caught:', event.error);
    
    // Log error to console with details
    console.group('Error Details');
    console.error('Message:', event.error.message);
    console.error('Stack:', event.error.stack);
    console.error('Source:', event.filename);
    console.error('Line:', event.lineno);
    console.error('Column:', event.colno);
    console.groupEnd();
    
    // Show error toast if toast function exists
    if (window.showToast && typeof window.showToast === 'function') {
        window.showToast('An error occurred. Please check console for details.', 'error');
    }
    
    // Prevent default error handling
    event.preventDefault();
});

// Set up promise rejection handling
window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
    
    // Log rejection to console with details
    console.group('Rejection Details');
    console.error('Reason:', event.reason);
    if (event.reason.stack) {
        console.error('Stack:', event.reason.stack);
    }
    console.groupEnd();
    
    // Show error toast if toast function exists
    if (window.showToast && typeof window.showToast === 'function') {
        window.showToast('A promise rejection occurred. Please check console for details.', 'error');
    }
    
    // Prevent default rejection handling
    event.preventDefault();
});

// Export helper functions
window.errorHandler = {
    /**
     * Safely execute a function with error handling
     * @param {Function} fn Function to execute
     * @param {Array} args Arguments to pass to function
     * @param {string} context Description of context for error reporting
     * @returns {any} Result of function or null if error
     */
    tryCatch: function(fn, args, context) {
        try {
            return fn.apply(this, args || []);
        } catch (error) {
            console.error(`Error in ${context || 'unknown context'}:`, error);
            if (window.showToast && typeof window.showToast === 'function') {
                window.showToast(`Error: ${error.message}`, 'error');
            }
            return null;
        }
    }
};

console.log('Global error handlers initialized');
