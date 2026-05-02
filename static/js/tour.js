// FlowSync Onboarding Tour (Phase 6)
document.addEventListener('DOMContentLoaded', () => {
    if (typeof Shepherd === 'undefined') return;

    const tour = new Shepherd.Tour({
        useModalOverlay: true,
        defaultStepOptions: {
            classes: 'flowsync-tour',
            scrollTo: { behavior: 'smooth', block: 'center' },
            cancelIcon: { enabled: true },
        }
    });

    tour.addStep({
        id: 'sidebar',
        title: 'Navigation Sidebar',
        text: 'This is your command center. Access Dashboard, Tasks, Projects, Team, Messages, and Analytics from here.',
        attachTo: { element: '#sidebar', on: 'right' },
        buttons: [{ text: 'Next →', action: tour.next }]
    });

    tour.addStep({
        id: 'new-task',
        title: 'Quick Task Creation',
        text: 'Click here anytime to create a new task from anywhere in the app.',
        attachTo: { element: '.btn-new-task', on: 'bottom' },
        buttons: [
            { text: '← Back', action: tour.back, secondary: true },
            { text: 'Next →', action: tour.next }
        ]
    });

    tour.addStep({
        id: 'main-content',
        title: 'Your Workspace',
        text: 'This is the main content area. On the Dashboard you\'ll see KPIs, tasks, and activity. Navigate to Tasks for the Kanban board.',
        attachTo: { element: '#main-content', on: 'left' },
        buttons: [
            { text: '← Back', action: tour.back, secondary: true },
            { text: 'Next →', action: tour.next }
        ]
    });

    tour.addStep({
        id: 'theme-toggle',
        title: 'Dark Mode',
        text: 'Toggle between light and dark themes here. Your preference is saved automatically.',
        attachTo: { element: '#theme-toggle', on: 'bottom' },
        buttons: [
            { text: '← Back', action: tour.back, secondary: true },
            { text: 'Get Started!', action: tour.complete }
        ]
    });

    tour.on('complete', async () => {
        try {
            await fetch('/api/v1/users/finish-tour', { method: 'POST', headers: { 'Content-Type': 'application/json' } });
        } catch (e) {}
    });

    tour.on('cancel', async () => {
        try {
            await fetch('/api/v1/users/finish-tour', { method: 'POST', headers: { 'Content-Type': 'application/json' } });
        } catch (e) {}
    });

    // Start tour after a short delay
    setTimeout(() => tour.start(), 800);
});
