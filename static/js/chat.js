// DOM elements and constants
const DOM = {
    chatContainer: document.getElementById('chat-container'),
    messageList: document.getElementById('message-list'),
    initialTextareaHeight: null
};

// Utility functions
const utils = {
    isMobileDevice() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    },

    scrollToBottom() {
        if (DOM.chatContainer) {
            DOM.chatContainer.scrollTop = DOM.chatContainer.scrollHeight;
        }
    }
};

// Form handling
const formHandler = {
    submit(form) {
        const textarea = form.querySelector('textarea');
        if (!textarea?.value.trim()) return;

        if (form.id === 'message-input-home') {
            form.submit();
        } else if (form.id === 'message-input-detail') {
            htmx.trigger(form, 'submit');
        }
        this.clearTextarea(textarea);
    },

    clearTextarea(textarea) {
        textarea.value = '';
        textarea.style.height = DOM.initialTextareaHeight || 'auto';
    },

    handleKeyPress(event) {
        if (!utils.isMobileDevice() && event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            const form = event.target.closest('form');
            form && formHandler.submit(form);
        }
    }
};

// Textarea management
const textareaManager = {
    setup(textarea) {
        // Auto-resize on input
        textarea.addEventListener('input', () => {
            textarea.style.height = 'auto';
            textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
        });

        // Handle enter key submission
        textarea.addEventListener('keypress', formHandler.handleKeyPress);

        // Store initial height if not already captured
        if (!DOM.initialTextareaHeight) {
            DOM.initialTextareaHeight = window.getComputedStyle(textarea).height;
        }
    }
};

// Form initialization
function initializeForms() {
    document.querySelectorAll('#message-input-home, #message-input-detail').forEach(form => {
        const textarea = form.querySelector('textarea');
        const submitButton = form.querySelector('button[type="submit"]');

        textarea && textareaManager.setup(textarea);

        submitButton?.addEventListener('click', (event) => {
            event.preventDefault();
            formHandler.submit(form);
        });
    });
}

// Message list observer setup
function setupMessageObserver(element, config = {}) {
    if (!element) return;

    const observer = new MutationObserver(() => utils.scrollToBottom());
    observer.observe(element, {
        childList: true,
        subtree: true,
        characterData: true,
        ...config
    });
}

// Event listeners
document.body.addEventListener('htmx:wsAfterSend', (evt) => {
    const textarea = evt.detail.elt.querySelector('textarea');
    textarea && formHandler.clearTextarea(textarea);
    utils.scrollToBottom();
});

document.body.addEventListener('htmx:afterOnLoad', (event) => {
    if (event.detail.elt.id === 'message-list') {
        utils.scrollToBottom();
    }
});

document.addEventListener('DOMContentLoaded', utils.scrollToBottom);
window.addEventListener('load', initializeForms);
document.body.addEventListener('htmx:afterSettle', initializeForms);

// Initialize observers
setupMessageObserver(DOM.messageList);
setupMessageObserver(DOM.chatContainer);

console.log('Chat management system initialized');
