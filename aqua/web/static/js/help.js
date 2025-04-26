/**
 * Aqua IoT Security Platform
 * Help & Support Page Functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Setup topic navigation
    setupTopicNavigation();
    
    // Setup support form
    setupSupportForm();
    
    // Setup live chat functionality
    setupLiveChat();
});

/**
 * Setup help topic navigation
 */
function setupTopicNavigation() {
    const topicLinks = document.querySelectorAll('.help-topics .list-group-item');
    const tabPanes = document.querySelectorAll('.tab-pane');
    
    topicLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Get the target tab id from href
            const targetId = this.getAttribute('href');
            
            // Hide all tab panes
            tabPanes.forEach(pane => {
                pane.classList.remove('show', 'active');
            });
            
            // Show the target tab pane
            const targetPane = document.querySelector(targetId);
            if (targetPane) {
                targetPane.classList.add('show', 'active');
            }
            
            // Update active link
            topicLinks.forEach(link => {
                link.classList.remove('active');
            });
            this.classList.add('active');
        });
    });
}

/**
 * Setup support form submission
 */
function setupSupportForm() {
    const submitSupportBtn = document.getElementById('submitSupportBtn');
    const supportForm = document.getElementById('supportForm');
    
    if (submitSupportBtn && supportForm) {
        submitSupportBtn.addEventListener('click', function() {
            // Check form validity
            if (!supportForm.checkValidity()) {
                supportForm.reportValidity();
                return;
            }
            
            // Get form data
            const subject = document.getElementById('supportSubject').value;
            const category = document.getElementById('supportCategory').value;
            const priority = document.getElementById('supportPriority').value;
            const message = document.getElementById('supportMessage').value;
            
            // In a real app, this would submit to an API
            console.log('Support ticket data:', { subject, category, priority, message });
            
            // Show success message
            showToast('Support ticket submitted successfully', 'success');
            
            // Close the modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('contactSupportModal'));
            modal.hide();
            
            // Reset the form
            supportForm.reset();
        });
    }
}

/**
 * Setup live chat functionality
 */
function setupLiveChat() {
    const liveChatBtn = document.getElementById('liveChatBtn');
    const liveChatWidget = document.getElementById('liveChatWidget');
    const closeChatBtn = document.getElementById('closeChatBtn');
    const chatMessageInput = document.getElementById('chatMessageInput');
    const sendChatBtn = document.getElementById('sendChatBtn');
    const chatMessages = document.querySelector('.chat-messages');
    
    if (liveChatBtn && liveChatWidget) {
        // Open chat widget
        liveChatBtn.addEventListener('click', function(e) {
            e.preventDefault();
            liveChatWidget.style.display = 'block';
            
            // Add welcome message after a delay to simulate agent joining
            setTimeout(() => {
                addChatMessage('Hello! This is Sarah from Aqua Support. How can I help you today?', 'agent');
            }, 2000);
        });
        
        // Close chat widget
        if (closeChatBtn) {
            closeChatBtn.addEventListener('click', function() {
                liveChatWidget.style.display = 'none';
            });
        }
        
        // Send message
        if (sendChatBtn && chatMessageInput) {
            sendChatBtn.addEventListener('click', sendChatMessage);
            chatMessageInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendChatMessage();
                }
            });
        }
    }
    
    // Function to send chat message
    function sendChatMessage() {
        const message = chatMessageInput.value.trim();
        
        if (message) {
            // Add user message to chat
            addChatMessage(message, 'user');
            
            // Clear input
            chatMessageInput.value = '';
            
            // Simulate agent response after a delay
            setTimeout(() => {
                const responses = [
                    "I understand your concern. Let me check on that for you.",
                    "That's a great question. Here's what you need to know...",
                    "I'd be happy to help with that. Could you provide more details?",
                    "Let me connect you with our technical team for further assistance.",
                    "We have documentation about that on our support site. I can send you a link."
                ];
                
                const randomResponse = responses[Math.floor(Math.random() * responses.length)];
                addChatMessage(randomResponse, 'agent');
            }, 2000);
        }
    }
    
    // Function to add message to chat
    function addChatMessage(message, sender) {
        const messageElement = document.createElement('div');
        messageElement.className = `chat-message ${sender}`;
        
        const timestamp = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
        
        messageElement.innerHTML = `
            <div class="message-content">${message}</div>
            <div class="message-time small text-muted">${timestamp}</div>
        `;
        
        chatMessages.appendChild(messageElement);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}
