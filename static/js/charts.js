// flowsync/static/js/charts.js
document.addEventListener('DOMContentLoaded', () => {
    if (typeof Chart === 'undefined') return;

    const cs = getComputedStyle(document.documentElement);
    const v = (n) => cs.getPropertyValue(n).trim();

    Chart.defaults.color = v('--text-2') || '#5c5a56';
    Chart.defaults.font.family = "'Inter', system-ui, sans-serif";
    Chart.defaults.font.size = 12;

    const colors = () => ({
        primary: v('--primary') || '#0e7c86',
        blue: v('--blue') || '#2563eb',
        purple: v('--purple') || '#7c3aed',
        orange: v('--orange') || '#ea580c',
        success: v('--success') || '#2d8a39',
        border: v('--border') || '#e8e5df'
    });

    let c = colors();

    async function loadWeeklyChart() {
        const ctx = document.getElementById('weekly-chart');
        if (!ctx) return;
        try {
            const data = await window.apiFetch('/analytics/api/weekly-completions');
            new Chart(ctx, {
                type: 'bar',
                data: { labels: data.labels, datasets: [{ label: 'Completed', data: data.values, backgroundColor: c.primary, borderRadius: 6 }] },
                options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true, grid: { color: c.border } }, x: { grid: { display: false } } }, plugins: { legend: { display: false } } }
            });
        } catch (e) { console.warn('Weekly chart error', e); }
    }

    async function loadProjectChart() {
        const ctx = document.getElementById('project-chart');
        if (!ctx) return;
        try {
            const data = await window.apiFetch('/analytics/api/project-distribution');
            new Chart(ctx, {
                type: 'doughnut',
                data: { labels: data.labels, datasets: [{ data: data.values, backgroundColor: [c.primary, c.blue, c.purple, c.orange, c.success], borderWidth: 0 }] },
                options: { responsive: true, maintainAspectRatio: false, cutout: '68%', plugins: { legend: { position: 'right', labels: { boxWidth: 10, padding: 12 } } } }
            });
        } catch (e) { console.warn('Project chart error', e); }
    }

    async function loadThroughputChart() {
        const ctx = document.getElementById('throughput-chart');
        if (!ctx) return;
        try {
            const data = await window.apiFetch('/analytics/api/team-throughput');
            new Chart(ctx, {
                type: 'bar',
                data: { labels: data.labels, datasets: [{ label: 'Completed', data: data.values, backgroundColor: c.blue, borderRadius: 6 }] },
                options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false, scales: { x: { beginAtZero: true, grid: { color: c.border } }, y: { grid: { display: false } } }, plugins: { legend: { display: false } } }
            });
        } catch (e) { console.warn('Throughput chart error', e); }
    }

    loadWeeklyChart();
    loadProjectChart();
    loadThroughputChart();
});
