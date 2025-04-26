/**
 * Aqua IoT Security Platform
 * Landing Page JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize navbar scrolling effect
    initNavbarScroll();
    
    // Smooth scrolling for anchor links
    initSmoothScrolling();
    
    // Initialize the contact form
    initContactForm();
    
    // Add animation to elements when they come into view
    initScrollAnimations();
});

/**
 * Handle navbar appearance on scroll
 */
function initNavbarScroll() {
    const navbar = document.querySelector('.navbar');
    
    if (!navbar) return;
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
}

/**
 * Enable smooth scrolling for anchor links
 */
function initSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (!targetElement) return;
            
            window.scrollTo({
                top: targetElement.offsetTop - 80,
                behavior: 'smooth'
            });
            
            // Update active nav link
            document.querySelectorAll('.navbar .nav-link').forEach(navLink => {
                navLink.classList.remove('active');
            });
            
            this.classList.add('active');
        });
    });
}

/**
 * Initialize contact form submission
 */
function initContactForm() {
    const contactForm = document.getElementById('contactForm');
    
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form data
            const name = document.getElementById('name').value;
            const email = document.getElementById('email').value;
            const subject = document.getElementById('subject').value;
            const message = document.getElementById('message').value;
            
            // Show success message (in a real implementation, you would send this data to a server)
            alert(`Thank you for your message, ${name}! We will get back to you soon.`);
            
            // Reset form
            contactForm.reset();
        });
    }
}

/**
 * Initialize animations on scroll
 */
function initScrollAnimations() {
    const animatedElements = document.querySelectorAll('.feature-card, .pricing-card, .process-step');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animated');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.2
    });
    
    animatedElements.forEach(el => {
        observer.observe(el);
    });
}
