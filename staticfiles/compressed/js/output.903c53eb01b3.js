;const themeToggleDarkIcon=document.getElementById('theme-toggle-dark-icon');const themeToggleLightIcon=document.getElementById('theme-toggle-light-icon');const themeToggleBtn=document.getElementById('theme-toggle');if(localStorage.getItem('color-theme')==='dark'||(!('color-theme'in localStorage)&&window.matchMedia('(prefers-color-scheme: dark)').matches)){themeToggleLightIcon.classList.remove('hidden');}else{themeToggleDarkIcon.classList.remove('hidden');}
themeToggleBtn.addEventListener('click',function(){themeToggleDarkIcon.classList.toggle('hidden');themeToggleLightIcon.classList.toggle('hidden');if(localStorage.getItem('color-theme')){if(localStorage.getItem('color-theme')==='light'){document.documentElement.classList.add('dark');localStorage.setItem('color-theme','dark');}else{document.documentElement.classList.remove('dark');localStorage.setItem('color-theme','light');}}else{if(document.documentElement.classList.contains('dark')){document.documentElement.classList.remove('dark');localStorage.setItem('color-theme','light');}else{document.documentElement.classList.add('dark');localStorage.setItem('color-theme','dark');}}});;document.addEventListener('DOMContentLoaded',function(){const toggleSidebarMobile=document.getElementById('toggleSidebarMobile');const sidebar=document.getElementById('sidebar');const sidebarBackdrop=document.getElementById('sidebarBackdrop');const toggleSidebarMobileHamburger=document.getElementById('toggleSidebarMobileHamburger');const toggleSidebarMobileClose=document.getElementById('toggleSidebarMobileClose');function toggleMobileSidebar(){sidebar.classList.toggle('hidden');sidebarBackdrop.classList.toggle('hidden');toggleSidebarMobileHamburger.classList.toggle('hidden');toggleSidebarMobileClose.classList.toggle('hidden');const isExpanded=toggleSidebarMobile.getAttribute('aria-expanded')==='true';toggleSidebarMobile.setAttribute('aria-expanded',String(!isExpanded));}
toggleSidebarMobile.addEventListener('click',toggleMobileSidebar);sidebarBackdrop.addEventListener('click',function(){sidebar.classList.add('hidden');sidebarBackdrop.classList.add('hidden');toggleSidebarMobileHamburger.classList.remove('hidden');toggleSidebarMobileClose.classList.add('hidden');toggleSidebarMobile.setAttribute('aria-expanded','false');});});document.addEventListener('DOMContentLoaded',function(){const sidebar=document.getElementById('sidebar');const mainContent=document.getElementById('main-content');const closeSidebarBtn=document.getElementById('closeSidebar');const openSidebarBtn=document.getElementById('opensidebar');const sidebarBackdrop=document.getElementById('sidebarBackdrop');function toggleSidebar(){sidebar.classList.toggle('-translate-x-full');sidebar.classList.toggle('w-64');sidebar.classList.toggle('w-0');mainContent.classList.toggle('lg:ml-64');mainContent.classList.toggle('lg:ml-0');sidebarBackdrop.classList.toggle('hidden');localStorage.setItem('sidebarOpen',sidebar.classList.contains('w-64'));}
function applySidebarState(){const sidebarOpen=localStorage.getItem('sidebarOpen')==='true';if(!sidebarOpen){sidebar.classList.add('-translate-x-full','w-0');sidebar.classList.remove('w-64');mainContent.classList.remove('lg:ml-64');mainContent.classList.add('lg:ml-0');sidebarBackdrop.classList.add('hidden');}}
closeSidebarBtn.addEventListener('click',toggleSidebar);openSidebarBtn.addEventListener('click',toggleSidebar);sidebarBackdrop.addEventListener('click',toggleSidebar);document.addEventListener('click',function(event){const isClickInsideSidebar=sidebar.contains(event.target);const isClickInsideToggleBtn=openSidebarBtn.contains(event.target);if(!isClickInsideSidebar&&!isClickInsideToggleBtn&&window.innerWidth<1024&&!sidebar.classList.contains('-translate-x-full')){toggleSidebar();}});applySidebarState();});;const chatContainer=document.getElementById('chat-container');const messageList=document.getElementById('message-list');let initialTextareaHeight;function isMobileDevice(){return/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);}
function submitForm(form){const textarea=form.querySelector('textarea');if(textarea&&textarea.value.trim()){if(form.id==='message-input-home'){form.submit();}else if(form.id==='message-input-detail'){htmx.trigger(form,'submit');}
clearTextareaAndResetHeight(textarea);scrollToBottom();}}
function handleKeyPress(event){if(!isMobileDevice()&&event.key==='Enter'&&!event.shiftKey){event.preventDefault();const form=event.target.closest('form');if(form){submitForm(form);}}}
function clearTextareaAndResetHeight(textarea){textarea.value="";resetTextareaHeight(textarea);}
function resetTextareaHeight(textarea){textarea.style.height='auto';textarea.style.height=initialTextareaHeight||(textarea.scrollHeight+'px');}
function scrollToBottom(){if(chatContainer){chatContainer.scrollTop=chatContainer.scrollHeight;}}
function isNearBottom(){const threshold=100;return chatContainer.scrollHeight-chatContainer.scrollTop-chatContainer.clientHeight<threshold;}
function setupTextarea(textarea){const minHeight=40;const maxHeight=200;function adjustHeight(){textarea.style.height='auto';textarea.style.height=Math.min(Math.max(textarea.scrollHeight,minHeight),maxHeight)+'px';}
textarea.addEventListener('input',adjustHeight);textarea.addEventListener('keypress',handleKeyPress);if(!initialTextareaHeight){initialTextareaHeight=window.getComputedStyle(textarea).height;}
adjustHeight();}
function initializeForms(){const forms=document.querySelectorAll('#message-input-home, #message-input-detail');forms.forEach(form=>{const textarea=form.querySelector('textarea');const submitButton=form.querySelector('button[type="submit"]');if(textarea){setupTextarea(textarea);}
if(submitButton){submitButton.addEventListener('click',(event)=>{event.preventDefault();submitForm(form);});}});}
document.body.addEventListener('htmx:wsAfterSend',function(evt){const textarea=evt.detail.elt.querySelector('textarea');if(textarea){clearTextareaAndResetHeight(textarea);}
scrollToBottom();});document.body.addEventListener('htmx:afterOnLoad',scrollToBottom);if(messageList){const observer=new MutationObserver(scrollToBottom);observer.observe(messageList,{childList:true,subtree:true,characterData:true});}
window.addEventListener('load',scrollToBottom);window.addEventListener('load',initializeForms);document.body.addEventListener('htmx:afterSettle',initializeForms);console.log('Updated form submission and textarea management script loaded');;