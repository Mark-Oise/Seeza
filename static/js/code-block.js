function copyCode(id) {
    const codeBlock = document.querySelector(`#code-block-${id} pre code`);
    const copyButton = document.querySelector(`#copy-button-${id} .copy-text`);
    
    if (codeBlock) {
        navigator.clipboard.writeText(codeBlock.textContent).then(() => {
            copyButton.textContent = 'Copied!';
            setTimeout(() => {
                copyButton.textContent = 'Copy';
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy text: ', err);
        });
    }
}