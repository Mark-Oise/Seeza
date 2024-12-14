;const themeToggleDarkIcon=document.getElementById('theme-toggle-dark-icon');const themeToggleLightIcon=document.getElementById('theme-toggle-light-icon');const themeToggleBtn=document.getElementById('theme-toggle');if(localStorage.getItem('color-theme')==='dark'||(!('color-theme'in localStorage)&&window.matchMedia('(prefers-color-scheme: dark)').matches)){themeToggleLightIcon.classList.remove('hidden');}else{themeToggleDarkIcon.classList.remove('hidden');}
themeToggleBtn.addEventListener('click',function(){themeToggleDarkIcon.classList.toggle('hidden');themeToggleLightIcon.classList.toggle('hidden');if(localStorage.getItem('color-theme')){if(localStorage.getItem('color-theme')==='light'){document.documentElement.classList.add('dark');localStorage.setItem('color-theme','dark');}else{document.documentElement.classList.remove('dark');localStorage.setItem('color-theme','light');}}else{if(document.documentElement.classList.contains('dark')){document.documentElement.classList.remove('dark');localStorage.setItem('color-theme','light');}else{document.documentElement.classList.add('dark');localStorage.setItem('color-theme','dark');}}});;const sidebar=document.getElementById('sidebar');const mainContent=document.getElementById('main-content');if(sidebar){const toggleSidebarMobile=()=>{sidebar.classList.toggle('hidden');sidebarBackdrop.classList.toggle('hidden');document.body.classList.toggle('overflow-hidden');}
const sidebarBackdrop=document.getElementById('sidebarBackdrop');const toggleSidebarMobileEl=document.getElementById('toggleSidebarMobile');const closeSidebarButton=document.getElementById('closeSidebar');toggleSidebarMobileEl?.addEventListener('click',toggleSidebarMobile);sidebarBackdrop?.addEventListener('click',toggleSidebarMobile);closeSidebarButton?.addEventListener('click',toggleSidebarMobile);const toggleSidebarDesktop=()=>{sidebar.classList.toggle('lg:w-64');sidebar.classList.toggle('lg:w-16');sidebar.classList.toggle('lg:translate-x-0');sidebar.classList.toggle('-lg:translate-x-full');mainContent.classList.toggle('lg:ml-64');mainContent.classList.toggle('lg:ml-16');document.body.classList.toggle('sidebar-expanded');const isExpanded=sidebar.classList.contains('lg:w-64');localStorage.setItem('sidebarExpanded',isExpanded);}
const applyStoredSidebarState=()=>{const isExpanded=localStorage.getItem('sidebarExpanded')==='true';if(isExpanded!==sidebar.classList.contains('lg:w-64')){toggleSidebarDesktop();}}
applyStoredSidebarState();closeSidebarButton?.addEventListener('click',(e)=>{if(window.innerWidth>=1024){e.preventDefault();toggleSidebarDesktop();}else{toggleSidebarMobile();}});};const chatContainer=document.getElementById('chat-container');const messageList=document.getElementById('message-list');let initialTextareaHeight;function isMobileDevice(){return/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);}
function submitForm(form){const textarea=form.querySelector('textarea');if(textarea&&textarea.value.trim()){if(form.id==='message-input-home'){form.submit();}else if(form.id==='message-input-detail'){htmx.trigger(form,'submit');}
clearTextareaAndResetHeight(textarea);}}
function handleKeyPress(event){if(!isMobileDevice()&&event.key==='Enter'&&!event.shiftKey){event.preventDefault();const form=event.target.closest('form');if(form){submitForm(form);}}}
function clearTextareaAndResetHeight(textarea){textarea.value="";resetTextareaHeight(textarea);}
function resetTextareaHeight(textarea){textarea.style.height='auto';textarea.style.height=initialTextareaHeight||(textarea.scrollHeight+'px');}
function scrollToBottom(){if(chatContainer){chatContainer.scrollTop=chatContainer.scrollHeight;}}
function setupTextarea(textarea){textarea.addEventListener('input',function(){this.style.height='auto';this.style.height=Math.min(this.scrollHeight,120)+'px';});textarea.addEventListener('keypress',handleKeyPress);if(!initialTextareaHeight){initialTextareaHeight=window.getComputedStyle(textarea).height;}}
function initializeForms(){const forms=document.querySelectorAll('#message-input-home, #message-input-detail');forms.forEach(form=>{const textarea=form.querySelector('textarea');const submitButton=form.querySelector('button[type="submit"]');if(textarea){setupTextarea(textarea);}
if(submitButton){submitButton.addEventListener('click',(event)=>{event.preventDefault();submitForm(form);});}});}
document.body.addEventListener('htmx:wsAfterSend',function(evt){const textarea=evt.detail.elt.querySelector('textarea');if(textarea){clearTextareaAndResetHeight(textarea);}
scrollToBottom();});document.addEventListener('DOMContentLoaded',scrollToBottom);document.body.addEventListener('htmx:afterSettle',scrollToBottom);if(messageList){const observer=new MutationObserver(scrollToBottom);observer.observe(messageList,{childList:true,subtree:true});}
window.addEventListener('load',initializeForms);document.body.addEventListener('htmx:afterSettle',initializeForms);console.log('Updated form submission and textarea management script loaded');;