// Core elements
const elements = {
    sidebar: document.getElementById('sidebar'),
    mainContent: document.getElementById('main-content'),
    backdrop: document.getElementById('sidebarBackdrop'),
    toggleMobile: document.getElementById('toggleSidebarMobile'),
    toggleDesktop: document.getElementById('toggleSidebarDesktop'),
    closeMobile: document.getElementById('closeSidebarMobile')
};

if (elements.sidebar) {
    // Mobile sidebar handling
    const toggleMobile = () => {
        const isHidden = elements.sidebar.classList.contains('-translate-x-full');
        elements.sidebar.classList.toggle('-translate-x-full', !isHidden);
        elements.backdrop.classList.toggle('hidden', !isHidden);
        document.body.classList.toggle('overflow-hidden', !isHidden);
    };

    // Desktop sidebar handling
    const toggleDesktop = () => {
        const isExpanded = !document.documentElement.classList.contains('sidebar-collapsed');
        document.documentElement.classList.toggle('sidebar-collapsed', isExpanded);
        localStorage.setItem('sidebarExpanded', !isExpanded);
    };

    // Event listeners
    elements.toggleMobile?.addEventListener('click', toggleMobile);
    elements.backdrop?.addEventListener('click', toggleMobile);
    elements.closeMobile?.addEventListener('click', toggleMobile);
    elements.toggleDesktop?.addEventListener('click', toggleDesktop);

    // Handle clicks outside sidebar on mobile
    document.addEventListener('click', (e) => {
        if (window.innerWidth < 1024 &&
            !elements.sidebar.contains(e.target) &&
            !e.target.closest('#toggleSidebarMobile')) {
            elements.sidebar.classList.add('-translate-x-full');
            elements.backdrop.classList.add('hidden');
            document.body.classList.remove('overflow-hidden');
        }
    });
}