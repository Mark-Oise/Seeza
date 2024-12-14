;const sidebar=document.getElementById('sidebar');const mainContent=document.getElementById('main-content');const sidebarBackdrop=document.getElementById('sidebarBackdrop');const toggleSidebarMobileEl=document.getElementById('toggleSidebarMobile');const closeSidebarEl=document.getElementById('closeSidebar');const toggleSidebarDesktopEl=document.getElementById('toggleSidebarDesktop');const closeSidebarMobileEl=document.getElementById('closeSidebarMobile');if(sidebar){const toggleSidebarMobile=()=>{if(sidebar.classList.contains('-translate-x-full')){sidebar.classList.remove('-translate-x-full');sidebarBackdrop.classList.remove('hidden');document.body.classList.add('overflow-hidden');}else{closeSidebarMobile();}}
toggleSidebarMobileEl?.addEventListener('click',toggleSidebarMobile);sidebarBackdrop?.addEventListener('click',toggleSidebarMobile);closeSidebarMobileEl?.addEventListener('click',toggleSidebarMobile);closeSidebarEl?.addEventListener('click',()=>{sidebar.classList.add('-translate-x-full');sidebarBackdrop.classList.add('hidden');document.body.classList.remove('overflow-hidden');sidebar.classList.remove('lg:translate-x-0');mainContent.classList.remove('lg:ml-64');mainContent.classList.add('lg:ml-0');document.body.classList.remove('sidebar-expanded');document.documentElement.classList.add('sidebar-collapsed');localStorage.setItem('sidebarExpanded',false);});const toggleSidebarDesktop=()=>{sidebar.classList.toggle('lg:translate-x-0');sidebar.classList.toggle('-translate-x-full');mainContent.classList.toggle('lg:ml-64');mainContent.classList.toggle('lg:ml-0');document.body.classList.toggle('sidebar-expanded');document.documentElement.classList.toggle('sidebar-collapsed');const isExpanded=sidebar.classList.contains('lg:translate-x-0');localStorage.setItem('sidebarExpanded',isExpanded);}
toggleSidebarDesktopEl?.addEventListener('click',toggleSidebarDesktop);const applySavedSidebarState=()=>{const savedSidebarState=localStorage.getItem('sidebarExpanded');if(savedSidebarState!==null&&window.innerWidth>=1024){const isExpanded=JSON.parse(savedSidebarState);if(!isExpanded){sidebar.classList.remove('lg:translate-x-0');sidebar.classList.add('-translate-x-full');mainContent.classList.remove('lg:ml-64');mainContent.classList.add('lg:ml-0');document.body.classList.remove('sidebar-expanded');document.documentElement.classList.add('sidebar-collapsed');}}}
applySavedSidebarState();setTimeout(applySavedSidebarState,50);function hideSidebarImmediately(){const savedSidebarState=localStorage.getItem('sidebarExpanded');if(savedSidebarState!==null&&!JSON.parse(savedSidebarState)){document.documentElement.classList.add('sidebar-collapsed');}}
hideSidebarImmediately();const closeSidebarMobile=()=>{if(window.innerWidth<1024){sidebar.classList.add('-translate-x-full');sidebarBackdrop.classList.add('hidden');document.body.classList.remove('overflow-hidden');}}
document.addEventListener('click',(event)=>{if(window.innerWidth<1024&&!sidebar.contains(event.target)&&!event.target.closest('#toggleSidebarMobile')){closeSidebarMobile();}});};const chatContainer=document.getElementById('chat-container');const messageList=document.getElementById('message-list');let initialTextareaHeight;function isMobileDevice(){return/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);}
function submitForm(form){const textarea=form.querySelector('textarea');if(textarea&&textarea.value.trim()){if(form.id==='message-input-home'){form.submit();}else if(form.id==='message-input-detail'){htmx.trigger(form,'submit');}
clearTextareaAndResetHeight(textarea);}}
function handleKeyPress(event){if(!isMobileDevice()&&event.key==='Enter'&&!event.shiftKey){event.preventDefault();const form=event.target.closest('form');if(form){submitForm(form);}}}
function clearTextareaAndResetHeight(textarea){textarea.value="";resetTextareaHeight(textarea);}
function resetTextareaHeight(textarea){textarea.style.height='auto';textarea.style.height=initialTextareaHeight||(textarea.scrollHeight+'px');}
function scrollToBottom(){if(chatContainer){chatContainer.scrollTop=chatContainer.scrollHeight;}}
function setupTextarea(textarea){textarea.addEventListener('input',function(){this.style.height='auto';this.style.height=Math.min(this.scrollHeight,120)+'px';});textarea.addEventListener('keypress',handleKeyPress);if(!initialTextareaHeight){initialTextareaHeight=window.getComputedStyle(textarea).height;}}
function initializeForms(){const forms=document.querySelectorAll('#message-input-home, #message-input-detail');forms.forEach(form=>{const textarea=form.querySelector('textarea');const submitButton=form.querySelector('button[type="submit"]');if(textarea){setupTextarea(textarea);}
if(submitButton){submitButton.addEventListener('click',(event)=>{event.preventDefault();submitForm(form);});}});}
document.body.addEventListener('htmx:wsAfterSend',function(evt){const textarea=evt.detail.elt.querySelector('textarea');if(textarea){clearTextareaAndResetHeight(textarea);scrollToBottom();}});document.addEventListener('DOMContentLoaded',scrollToBottom);if(messageList){const observer=new MutationObserver((mutations)=>{for(const mutation of mutations){if(mutation.type==='childList'&&mutation.addedNodes.length>0){scrollToBottom();break;}}});observer.observe(messageList,{childList:true,subtree:true});}
window.addEventListener('load',initializeForms);document.body.addEventListener('htmx:afterSettle',initializeForms);console.log('Updated form submission and textarea management script loaded');;function applySyntaxHighlighting(element=document){element.querySelectorAll('pre code').forEach((block)=>{hljs.highlightElement(block);});}
document.addEventListener('DOMContentLoaded',()=>{applySyntaxHighlighting();});document.body.addEventListener('htmx:afterSwap',(event)=>{applySyntaxHighlighting(event.detail.elt);});document.body.addEventListener('htmx:wsAfterMessage',()=>{applySyntaxHighlighting();});;