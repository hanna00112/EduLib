class ChatBot {
    constructor() {
        this.chatContainer = document.querySelector('.chat-container');
        this.chatMessages = document.getElementById('chatMessages');
        this.userInput = document.getElementById('userInput');
        this.sendButton = document.getElementById('sendMessage');
        this.toggleButton = document.getElementById('toggleChat');
        this.clearButton = document.getElementById('clearChat');
        this.toggleChatButton = document.getElementById('toggleChatButton');
        this.suggestionChips = document.querySelectorAll('.chip');
        
        this.initializeEventListeners();
        this.adjustTextareaHeight();
    }

    initializeEventListeners() {
        // Send message events
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Auto-resize textarea
        this.userInput.addEventListener('input', () => this.adjustTextareaHeight());

        // Toggle chat visibility
        this.toggleButton.addEventListener('click', () => this.toggleChat());
        this.toggleChatButton.addEventListener('click', () => this.toggleChat());

        // Clear chat
        this.clearButton.addEventListener('click', () => this.clearChat());

        // Suggestion chips
        this.suggestionChips.forEach(chip => {
            chip.addEventListener('click', () => {
                this.userInput.value = chip.textContent;
                this.sendMessage();
            });
        });
    }

    adjustTextareaHeight() {
        this.userInput.style.height = 'auto';
        this.userInput.style.height = (this.userInput.scrollHeight) + 'px';
    }

    async sendMessage() {
        const message = this.userInput.value.trim();
        if (!message) return;

        // Add user message to chat
        this.addMessage(message, 'user');
        this.userInput.value = '';
        this.adjustTextareaHeight();

        // Show typing indicator
        this.showTypingIndicator();

        try {
            const response = await fetch('/chatbot', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });

            const data = await response.json();
            
            // Remove typing indicator and add bot response
            this.removeTypingIndicator();
            this.addMessage(data.response, 'bot');

        } catch (error) {
            this.removeTypingIndicator();
            this.addMessage('Sorry, I encountered an error. Please try again later.', 'bot');
            console.error('Error:', error);
        }
    }

    addMessage(content, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;

        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.innerHTML = sender === 'user' ? 
            '<i class="fas fa-user"></i>' : 
            '<i class="fas fa-robot"></i>';

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.textContent = content;

        const messageTime = document.createElement('div');
        messageTime.className = 'message-time';
        messageTime.textContent = this.getCurrentTime();

        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);
        messageDiv.appendChild(messageTime);

        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot-message typing-indicator';
        typingDiv.innerHTML = `
            <div class="avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;
        this.chatMessages.appendChild(typingDiv);
        this.scrollToBottom();
    }

    removeTypingIndicator() {
        const typingIndicator = this.chatMessages.querySelector('.typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    getCurrentTime() {
        return new Date().toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }

    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    toggleChat() {
        this.chatContainer.classList.toggle('minimized');
        const icon = this.toggleButton.querySelector('i');
        icon.classList.toggle('fa-minus');
        icon.classList.toggle('fa-plus');
    }

    clearChat() {
        while (this.chatMessages.firstChild) {
            this.chatMessages.removeChild(this.chatMessages.firstChild);
        }
        // Add initial bot message
        this.addMessage('Hello! I\'m your library assistant. How can I help you today?', 'bot');
    }
}

// Initialize chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const chatbot = new ChatBot();
});