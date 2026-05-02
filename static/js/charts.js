// flowsync/static/js/charts.js

document.addEventListener('DOMContentLoaded', () => {
    if (typeof Chart === 'undefined') return;

    // Common Chart.js options for the theme
    Chart.defaults.color = getComputedStyle(document.documentElement).getPropertyValue('--color-text-muted').trim() || '#7a7974';
    Chart.defaults.font.family = getComputedStyle(document.documentElement).getPropertyValue('--font-body').trim() || 'Inter, sans-serif';

    const getThemeColors = () => ({
        primary: getComputedStyle(document.documentElement).getPropertyValue('--color-primary').trim(),
        primaryHighlight: getComputedStyle(document.documentElement).getPropertyValue('--color-primary-highlight').trim(),
        surfaceOffset: getComputedStyle(document.documentElement).getPropertyValue('--color-surface-offset').trim(),
        border: getComputedStyle(document.documentElement).getPropertyValue('--color-border').trim(),
        blue: getComputedStyle(document.documentElement).getPropertyValue('--color-blue').trim(),
        purple: getComputedStyle(document.documentElement).getPropertyValue('--color-purple').trim(),
        orange: getComputedStyle(document.documentElement).getPropertyValue('--color-orange').trim(),
        success: getComputedStyle(document.documentElement).getPropertyValue('--color-success').trim()
    });

    let colors = getThemeColors();
    const chartInstances = {};

    async function loadWeeklyChart() {
        const ctx = document.getElementById('weekly-chart');
        if (!ctx) return;
        
        const data = await window.apiFetch('/analytics/api/weekly-completions');
        chartInstances['weekly'] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Completed Tasks',
                    data: data.values,
                    backgroundColor: colors.primary,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true, grid: { color: colors.border } },
                    x: { grid: { display: false } }
                }
            }
        });
    }

    async function loadProjectChart() {
        const ctx = document.getElementById('project-chart');
        if (!ctx) return;
        
        const data = await window.apiFetch('/analytics/api/project-distribution');
        chartInstances['project'] = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.values,
                    backgroundColor: [colors.primary, colors.blue, colors.purple, colors.orange, colors.success],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: { legend: { position: 'right' } }
            }
        });
    }

    async function loadThroughputChart() {
        const ctx = document.getElementById('throughput-chart');
        if (!ctx) return;
        
        const data = await window.apiFetch('/analytics/api/team-throughput');
        chartInstances['throughput'] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Tasks/Person',
                    data: data.values,
                    backgroundColor: colors.blue,
                    borderRadius: 4
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { beginAtZero: true, grid: { color: colors.border } },
                    y: { grid: { display: false } }
                }
            }
        });
    }

    // Re-render on theme change
    window.addEventListener('themeChanged', () => {
        colors = getThemeColors();
        Chart.defaults.color = getComputedStyle(document.documentElement).getPropertyValue('--color-text-muted').trim();
        
        if (chartInstances['weekly']) {
            chartInstances['weekly'].data.datasets[0].backgroundColor = colors.primary;
            chartInstances['weekly'].options.scales.y.grid.color = colors.border;
            chartInstances['weekly'].update();
        }
        if (chartInstances['project']) {
            chartInstances['project'].data.datasets[0].backgroundColor = [colors.primary, colors.blue, colors.purple, colors.orange, colors.success];
            chartInstances['project'].update();
        }
        if (chartInstances['throughput']) {
            chartInstances['throughput'].data.datasets[0].backgroundColor = colors.blue;
            chartInstances['throughput'].options.scales.x.grid.color = colors.border;
            chartInstances['throughput'].update();
        }
    });

    loadWeeklyChart();
    loadProjectChart();
    loadThroughputChart();
});
