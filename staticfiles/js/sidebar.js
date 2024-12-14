const sidebar = document.getElementById('sidebar');
const mainContent = document.getElementById('main-content');
const sidebarBackdrop = document.getElementById('sidebarBackdrop');
const toggleSidebarMobileEl = document.getElementById('toggleSidebarMobile');
const closeSidebarEl = document.getElementById('closeSidebar');
const toggleSidebarDesktopEl = document.getElementById('toggleSidebarDesktop');
const closeSidebarMobileEl = document.getElementById('closeSidebarMobile');

if (sidebar) {
    const toggleSidebarMobile = () => {
        if (sidebar.classList.contains('-translate-x-full')) {
            sidebar.classList.remove('-translate-x-full');
            sidebarBackdrop.classList.remove('hidden');
            document.body.classList.add('overflow-hidden');
        } else {
            closeSidebarMobile();
        }
    }

    // Mobile toggle
    toggleSidebarMobileEl?.addEventListener('click', toggleSidebarMobile);

    // Backdrop click to close
    sidebarBackdrop?.addEventListener('click', toggleSidebarMobile);

    // Close sidebar mobile button
    closeSidebarMobileEl?.addEventListener('click', toggleSidebarMobile);

    // Close sidebar button
    closeSidebarEl?.addEventListener('click', () => {
        sidebar.classList.add('-translate-x-full');
        sidebarBackdrop.classList.add('hidden');
        document.body.classList.remove('overflow-hidden');
        // Remove desktop-specific classes
        sidebar.classList.remove('lg:translate-x-0');
        mainContent.classList.remove('lg:ml-64');
        mainContent.classList.add('lg:ml-0');
        document.body.classList.remove('sidebar-expanded');
        document.documentElement.classList.add('sidebar-collapsed');
        localStorage.setItem('sidebarExpanded', false);
    });

    // Desktop toggle
    const toggleSidebarDesktop = () => {
        sidebar.classList.toggle('lg:translate-x-0');
        sidebar.classList.toggle('-translate-x-full');
        mainContent.classList.toggle('lg:ml-64');
        mainContent.classList.toggle('lg:ml-0');
        document.body.classList.toggle('sidebar-expanded');
        document.documentElement.classList.toggle('sidebar-collapsed');
        
        // Save sidebar state to localStorage
        const isExpanded = sidebar.classList.contains('lg:translate-x-0');
        localStorage.setItem('sidebarExpanded', isExpanded);
    }

    toggleSidebarDesktopEl?.addEventListener('click', toggleSidebarDesktop);

    // Modify applySavedSidebarState to only apply on desktop
    const applySavedSidebarState = () => {
        const savedSidebarState = localStorage.getItem('sidebarExpanded');
        if (savedSidebarState !== null && window.innerWidth >= 1024) {
            const isExpanded = JSON.parse(savedSidebarState);
            if (!isExpanded) {
                sidebar.classList.remove('lg:translate-x-0');
                sidebar.classList.add('-translate-x-full');
                mainContent.classList.remove('lg:ml-64');
                mainContent.classList.add('lg:ml-0');
                document.body.classList.remove('sidebar-expanded');
                document.documentElement.classList.add('sidebar-collapsed');
            }
        }
    }

    // Apply saved state immediately and after a short delay
    applySavedSidebarState();
    setTimeout(applySavedSidebarState, 50);

    // Function to hide sidebar immediately if it was previously collapsed
    function hideSidebarImmediately() {
        const savedSidebarState = localStorage.getItem('sidebarExpanded');
        if (savedSidebarState !== null && !JSON.parse(savedSidebarState)) {
            document.documentElement.classList.add('sidebar-collapsed');
        }
    }

    // Call this function as early as possible
    hideSidebarImmediately();

    // Function to close sidebar on mobile
    const closeSidebarMobile = () => {
        if (window.innerWidth < 1024) {
            sidebar.classList.add('-translate-x-full');
            sidebarBackdrop.classList.add('hidden');
            document.body.classList.remove('overflow-hidden');
        }
    }

    // Event listener for clicks outside the sidebar
    document.addEventListener('click', (event) => {
        if (window.innerWidth < 1024 && 
            !sidebar.contains(event.target) && 
            !event.target.closest('#toggleSidebarMobile')) {
            closeSidebarMobile();
        }
    });
}