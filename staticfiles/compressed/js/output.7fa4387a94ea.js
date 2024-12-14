;const chatContainer=document.getElementById('chat-container');const messageList=document.getElementById('message-list');let initialTextareaHeight;function isMobileDevice(){return/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);}
function submitForm(form){const textarea=form.querySelector('textarea');if(textarea&&textarea.value.trim()){if(form.id==='message-input-home'){form.submit();}else if(form.id==='message-input-detail'){htmx.trigger(form,'submit');}
clearTextareaAndResetHeight(textarea);}}
function handleKeyPress(event){if(!isMobileDevice()&&event.key==='Enter'&&!event.shiftKey){event.preventDefault();const form=event.target.closest('form');if(form){submitForm(form);}}}
function clearTextareaAndResetHeight(textarea){textarea.value="";resetTextareaHeight(textarea);}
function resetTextareaHeight(textarea){textarea.style.height='auto';textarea.style.height=initialTextareaHeight||`${textarea.scrollHeight}px`;}
function scrollToBottom(){if(chatContainer){chatContainer.scrollTop=chatContainer.scrollHeight;}}
function isNearBottom(){const threshold=100;return chatContainer.scrollHeight-chatContainer.scrollTop-chatContainer.clientHeight<threshold;}
function setupTextarea(textarea){const minHeight=40;const maxHeight=200;function adjustHeight(){textarea.style.height='auto';textarea.style.height=`${Math.min(Math.max(textarea.scrollHeight, minHeight), maxHeight)}px`;}
textarea.addEventListener('input',adjustHeight);textarea.addEventListener('keypress',handleKeyPress);if(!initialTextareaHeight){initialTextareaHeight=window.getComputedStyle(textarea).height;}
adjustHeight();}
function initializeForms(){const forms=document.querySelectorAll('#message-input-home, #message-input-detail');forms.forEach(form=>{const textarea=form.querySelector('textarea');const submitButton=form.querySelector('button[type="submit"]');if(textarea){setupTextarea(textarea);}
if(submitButton){submitButton.addEventListener('click',(event)=>{event.preventDefault();submitForm(form);});}});}
document.body.addEventListener('htmx:wsAfterSend',(evt)=>{const textarea=evt.detail.elt.querySelector('textarea');if(textarea){clearTextareaAndResetHeight(textarea);}
if(isNearBottom()){scrollToBottom();}});document.body.addEventListener('htmx:afterOnLoad',()=>{if(isNearBottom()){scrollToBottom();}});if(messageList){const observer=new MutationObserver(()=>{if(isNearBottom()){scrollToBottom();}});observer.observe(messageList,{childList:true,subtree:true});}
window.addEventListener('load',scrollToBottom);window.addEventListener('load',initializeForms);document.body.addEventListener('htmx:afterSettle',initializeForms);console.log('Updated form submission and textarea management script loaded');;