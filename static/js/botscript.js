document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-btn');
    const chatContainer = document.querySelector('.chat-container');
    const chatToggleBtn = document.querySelector('.chat-toggle-btn');
    const minimizeBtn = document.querySelector('.minimize-btn');
    const closeBtn = document.querySelector('.close-btn');
    const typingIndicator = document.querySelector('.typing-indicator');

    // Chat state
    let isChatOpen = false;
    
    // Event Listeners
    chatToggleBtn.addEventListener('click', toggleChat);
    minimizeBtn.addEventListener('click', toggleChat);
    closeBtn.addEventListener('click', toggleChat);
    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Toggle chat window
    function toggleChat() {
        isChatOpen = !isChatOpen;
        chatContainer.style.display = isChatOpen ? 'flex' : 'none';
        chatToggleBtn.style.display = isChatOpen ? 'none' : 'block';
    }

    // Add message to chat
    function addMessage(message, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = message;
        
        const timestampDiv = document.createElement('div');
        timestampDiv.className = 'message-timestamp';
        timestampDiv.textContent = new Date().toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        messageDiv.appendChild(contentDiv);
        messageDiv.appendChild(timestampDiv);
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Show/hide typing indicator
    function toggleTypingIndicator(show) {
        typingIndicator.style.display = show ? 'flex' : 'none';
    }

    // Send message to backend
    // Add better error handling and logging
async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    // Add user message to chat
    addMessage(message, true);
    userInput.value = '';

    // Show typing indicator
    toggleTypingIndicator(true);

    try {
        const response = await fetch('/chatbot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });

        console.log('Response status:', response.status); // Debug log

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('Response data:', data); // Debug log

        // Hide typing indicator
        toggleTypingIndicator(false);

        if (data.response) {
            // Add bot response to chat
            addMessage(data.response);
        } else {
            addMessage('Received empty response from server');
        }
    } catch (error) {
        console.error('Detailed error:', error); // Debug log
        toggleTypingIndicator(false);
        addMessage(`Error: ${error.message}`);
    }
}

    // Initialize chat window state
    chatContainer.style.display = 'none';
});