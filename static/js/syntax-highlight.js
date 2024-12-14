// Function to apply syntax highlighting
function applySyntaxHighlighting(element = document) {
    element.querySelectorAll('pre code').forEach((block) => {
        hljs.highlightElement(block);
    });
}

// Apply highlighting on initial page load
document.addEventListener('DOMContentLoaded', () => {
    applySyntaxHighlighting();
});

// Re-apply highlighting after HTMX content swaps
document.body.addEventListener('htmx:afterSwap', (event) => {
    applySyntaxHighlighting(event.detail.elt);
});

// Re-apply highlighting after WebSocket messages (for real-time updates)
document.body.addEventListener('htmx:wsAfterMessage', () => {
    applySyntaxHighlighting();
});