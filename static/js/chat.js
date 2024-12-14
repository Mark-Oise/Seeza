// DOM elements
const chatContainer = document.getElementById('chat-container');
const messageList = document.getElementById('message-list');

// Initial textarea height
let initialTextareaHeight;

// Function to detect if the device is mobile
function isMobileDevice() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}

// Function to handle form submission
function submitForm(form) {
    const textarea = form.querySelector('textarea');
    if (textarea && textarea.value.trim()) {
        if (form.id === 'message-input-home') {
            form.submit();
        } else if (form.id === 'message-input-detail') {
            htmx.trigger(form, 'submit');
        }
        clearTextareaAndResetHeight(textarea);
    }
}

// Function to handle keypress events
function handleKeyPress(event) {
    if (!isMobileDevice() && event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        const form = event.target.closest('form');
        if (form) {
            submitForm(form);
        }
    }
}

// Function to clear textarea and reset height
function clearTextareaAndResetHeight(textarea) {
    textarea.value = "";
    resetTextareaHeight(textarea);
}

// Function to reset textarea height
function resetTextareaHeight(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = initialTextareaHeight || (textarea.scrollHeight + 'px');
}

// Modify the scrollToBottom function
function scrollToBottom() {
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
}

// Function to set up textarea behavior
function setupTextarea(textarea) {
    // Adjust textarea height on input
    textarea.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 120) + 'px';
    });

    // Add keypress event listener for form submission (desktop only)
    textarea.addEventListener('keypress', handleKeyPress);

    // Capture initial height
    if (!initialTextareaHeight) {
        initialTextareaHeight = window.getComputedStyle(textarea).height;
    }
}

// Function to initialize forms
function initializeForms() {
    const forms = document.querySelectorAll('#message-input-home, #message-input-detail');

    forms.forEach(form => {
        const textarea = form.querySelector('textarea');
        const submitButton = form.querySelector('button[type="submit"]');

        if (textarea) {
            setupTextarea(textarea);
        }

        if (submitButton) {
            submitButton.addEventListener('click', (event) => {
                event.preventDefault();
                submitForm(form);
            });
        }
    });
}

// HTMX specific event listeners
document.body.addEventListener('htmx:wsAfterSend', function(evt) {
    const textarea = evt.detail.elt.querySelector('textarea');
    if (textarea) {
        clearTextareaAndResetHeight(textarea);
    }
    scrollToBottom(); // Add this line to scroll after sending a message
});

// Call scrollToBottom on page load
document.addEventListener('DOMContentLoaded', scrollToBottom);

// Create a MutationObserver to watch for changes in the message list
if (messageList) {
    const observer = new MutationObserver((mutations) => {
        for (let mutation of mutations) {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                scrollToBottom();
                break;
            }
        }
    });
    observer.observe(messageList, { childList: true });
}

// Add a specific event listener for new message additions
document.body.addEventListener('htmx:afterOnLoad', (event) => {
    if (event.detail.elt.id === 'message-list') {
        scrollToBottom();
    }
});

// Initialize on page load and after HTMX content loads
window.addEventListener('load', initializeForms);
document.body.addEventListener('htmx:afterSettle', initializeForms);

console.log('Updated form submission and textarea management script loaded');

// Modify the MutationObserver setup
if (messageList) {
    const observer = new MutationObserver((mutations) => {
        for (let mutation of mutations) {
            if (mutation.type === 'childList' || mutation.type === 'characterData') {
                scrollToBottom();
                break;
            }
        }
    });
    observer.observe(messageList, { 
        childList: true, 
        subtree: true, 
        characterData: true 
    });
}

// Modify the handleContentChange function
function handleContentChange(mutationsList, observer) {
    for (let mutation of mutationsList) {
        if (mutation.type === 'childList' || mutation.type === 'characterData') {
            scrollToBottom();
            break;
        }
    }
}

// Set up the MutationObserver on the chat-container instead
if (chatContainer) {
    const observer = new MutationObserver(handleContentChange);
    observer.observe(chatContainer, { 
        childList: true, 
        subtree: true, 
        characterData: true 
    });
}

// ... rest of the existing code ...











