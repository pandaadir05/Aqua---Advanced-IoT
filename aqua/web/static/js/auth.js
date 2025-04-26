/**
 * Aqua IoT Security Platform
 * Authentication Pages Functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Handle password strength on register page
    setupPasswordStrength();
    
    // Form validation
    setupFormValidation();
    
    // Check for dark mode preference
    applyDarkMode();
});

/**
 * Setup password strength meter
 */
function setupPasswordStrength() {
    const passwordInput = document.getElementById('password');
    const passwordStrength = document.getElementById('passwordStrength');
    
    if (passwordInput && passwordStrength) {
        passwordInput.addEventListener('input', function() {
            const password = this.value;
            
            // Remove animation class if exists
            passwordStrength.classList.remove('animate');
            
            // Reset classes
            passwordStrength.className = 'password-strength';
            
            if (password.length === 0) {
                passwordStrength.style.width = '0';
                return;
            }
            
            // Check password strength
            let strength = 0;
            
            // Length check
            if (password.length >= 8) strength += 1;
            if (password.length >= 12) strength += 1;
            
            // Character variety checks
            if (/[A-Z]/.test(password)) strength += 1;
            if (/[a-z]/.test(password)) strength += 1;
            if (/[0-9]/.test(password)) strength += 1;
            if (/[^A-Za-z0-9]/.test(password)) strength += 1;
            
            // Update UI
            if (strength < 3) {
                passwordStrength.classList.add('weak');
            } else if (strength < 5) {
                passwordStrength.classList.add('medium');
            } else {
                passwordStrength.classList.add('strong');
            }
            
            // Add animation class after a small delay
            setTimeout(() => {
                passwordStrength.classList.add('animate');
            }, 10);
        });
    }
}

/**
 * Setup form validation
 */
function setupFormValidation() {
    const registerForm = document.getElementById('registerForm');
    const loginForm = document.getElementById('loginForm');
    
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirmPassword').value;
            
            if (password !== confirmPassword) {
                e.preventDefault();
                alert('Passwords do not match!');
                return false;
            }
            
            // Add any other custom validation here
            return true;
        });
    }
    
    if (loginForm) {
        // Any custom login form validation can go here
    }
}

/**
 * Apply dark mode if user preference exists
 */
function applyDarkMode() {
    // Check for saved mode
    const storedTheme = localStorage.getItem('theme');
    
    // Check system preferences
    const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
    
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
    if (isDarkMode) {
        document.body.classList.add('dark-mode');
    } else {
        document.body.classList.remove('dark-mode');
    }
}
