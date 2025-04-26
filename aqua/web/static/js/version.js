/**
 * Aqua IoT Security Platform
 * Version Management - Prevents 304 Not Modified issues with scripts
 */

const SITE_VERSION = '1.1.0';

// Add version parameter to all script and stylesheet URLs
document.addEventListener('DOMContentLoaded', function() {
    // Add version to dynamically loaded scripts
    const originalCreateElement = document.createElement;
    document.createElement = function(tag) {
        const element = originalCreateElement.call(document, tag);
        
        if (tag.toLowerCase() === 'script') {
            const originalSetAttribute = element.setAttribute;
            element.setAttribute = function(name, value) {
                if (name === 'src' && value.startsWith('/static/') && !value.includes('?v=')) {
                    value = value + '?v=' + SITE_VERSION;
                }
                return originalSetAttribute.call(this, name, value);
            };
        }
        
        return element;
    };
    
    // Function to add version to fetch requests
    const originalFetch = window.fetch;
    window.fetch = function(url, options) {
        if (typeof url === 'string' && url.startsWith('/api/')) {
            // Add cache busting parameter to API calls
            const separator = url.includes('?') ? '&' : '?';
            url = url + separator + '_=' + Date.now();
        }
        return originalFetch.call(this, url, options);
    };
    
    console.log('Version management initialized: ' + SITE_VERSION);
});
