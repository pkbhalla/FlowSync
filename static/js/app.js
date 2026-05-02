// flowsync/static/js/app.js

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initModals();
    initSidebar();
    initLucide();
    highlightNav();
});

function initTheme() {
    const btn = document.getElementById('theme-toggle');
    if (!btn) return;

    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);

    btn.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        
        // Trigger event for charts
        window.dispatchEvent(new Event('themeChanged'));
    });
}

function initModals() {
    const modalTriggers = document.querySelectorAll('[data-modal-target]');
    const closeBtns = document.querySelectorAll('[data-modal-close]');

    modalTriggers.forEach(trigger => {
        trigger.addEventListener('click', () => {
            const modalId = trigger.getAttribute('data-modal-target');
            openModal(modalId);
        });
    });

    closeBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const modal = e.target.closest('.modal-backdrop');
            if (modal) {
                closeModal(modal.id);
            }
        });
    });

    document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
        backdrop.addEventListener('click', (e) => {
            if (e.target === backdrop) {
                closeModal(backdrop.id);
            }
        });
    });
}

function openModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.classList.add('show');
    }
}

function closeModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.classList.remove('show');
    }
}

function initSidebar() {
    const toggle = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');
    if (toggle && sidebar) {
        toggle.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });
    }
}

function initLucide() {
    if (window.lucide) {
        window.lucide.createIcons();
    }
}

function highlightNav() {
    const path = window.location.pathname;
    const navLinks = document.querySelectorAll('.sidebar-nav a');
    navLinks.forEach(link => {
        if (link.getAttribute('href') === path || 
           (path.startsWith(link.getAttribute('href')) && link.getAttribute('href') !== '/')) {
            link.classList.add('active');
        } else if (path === '/' && link.getAttribute('href') === '/') {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

function showToast(message, type = 'success') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    if (type === 'error') toast.style.borderLeftColor = 'var(--color-error)';
    if (type === 'info') toast.style.borderLeftColor = 'var(--color-blue)';
    
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

async function apiFetch(url, options = {}) {
    try {
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
        const method = (options.method || 'GET').toUpperCase();
        const mutating = ['POST', 'PUT', 'PATCH', 'DELETE'].includes(method);
        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...(mutating && csrfToken ? { 'X-CSRFToken': csrfToken } : {}),
                ...options.headers
            }
        });
        
        const data = await response.json().catch(() => null);
        
        if (!response.ok) {
            throw new Error(data?.message || `Error ${response.status}`);
        }
        
        return data;
    } catch (error) {
        showToast(error.message, 'error');
        throw error;
    }
}
window.apiFetch = apiFetch;
window.showToast = showToast;
window.openModal = openModal;
window.closeModal = closeModal;
