// Emotion Analytics and Charting
class EmotionChart {
    constructor() {
        this.apiBase = 'http://localhost:8000';
        this.charts = {};
        this.init();
    }

    init() {
        this.setupCharts();
        this.loadAnalytics();
    }

    setupCharts() {
        // Create mood chart
        this.createMoodChart();
        this.createEmotionDistributionChart();
        this.createTrendChart();
    }

    async loadAnalytics() {
        try {
            const response = await fetch(`${this.apiBase}/mood-analytics/default`);
            const analytics = await response.json();
            this.updateCharts(analytics);
        } catch (error) {
            console.error('Error loading analytics:', error);
        }
    }

    createMoodChart() {
        const canvas = document.getElementById('mood-chart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        
        // Sample data for initial display
        const data = {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'Mood Score',
                data: [7, 6, 8, 5, 9, 7, 8],
                borderColor: '#6366f1',
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                tension: 0.4,
                fill: true
            }]
        };

        const config = {
            type: 'line',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 10,
                        ticks: {
                            color: '#cbd5e1'
                        },
                        grid: {
                            color: '#475569'
                        }
                    },
                    x: {
                        ticks: {
                            color: '#cbd5e1'
                        },
                        grid: {
                            color: '#475569'
                        }
                    }
                }
            }
        };

        this.charts.mood = new Chart(ctx, config);
    }

    createEmotionDistributionChart() {
        const canvas = document.getElementById('emotion-distribution-chart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        
        const data = {
            labels: ['Happy', 'Sad', 'Angry', 'Fear', 'Surprise', 'Neutral'],
            datasets: [{
                data: [30, 15, 10, 5, 20, 20],
                backgroundColor: [
                    '#10b981',
                    '#3b82f6',
                    '#ef4444',
                    '#f59e0b',
                    '#f97316',
                    '#6b7280'
                ],
                borderWidth: 0
            }]
        };

        const config = {
            type: 'doughnut',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#cbd5e1',
                            padding: 20
                        }
                    }
                }
            }
        };

        this.charts.distribution = new Chart(ctx, config);
    }

    createTrendChart() {
        const canvas = document.getElementById('trend-chart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        
        const data = {
            labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
            datasets: [{
                label: 'Average Mood',
                data: [6.5, 7.2, 6.8, 7.5],
                borderColor: '#8b5cf6',
                backgroundColor: 'rgba(139, 92, 246, 0.1)',
                tension: 0.4,
                fill: true
            }]
        };

        const config = {
            type: 'line',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 10,
                        ticks: {
                            color: '#cbd5e1'
                        },
                        grid: {
                            color: '#475569'
                        }
                    },
                    x: {
                        ticks: {
                            color: '#cbd5e1'
                        },
                        grid: {
                            color: '#475569'
                        }
                    }
                }
            }
        };

        this.charts.trend = new Chart(ctx, config);
    }

    updateCharts(analytics) {
        if (analytics.emotion_counts && this.charts.distribution) {
            const labels = Object.keys(analytics.emotion_counts);
            const data = Object.values(analytics.emotion_counts);
            
            this.charts.distribution.data.labels = labels;
            this.charts.distribution.data.datasets[0].data = data;
            this.charts.distribution.update();
        }

        if (analytics.trends && analytics.trends.daily_trends && this.charts.mood) {
            const dailyData = analytics.trends.daily_trends;
            const labels = Object.keys(dailyData);
            const values = Object.values(dailyData);
            
            this.charts.mood.data.labels = labels;
            this.charts.mood.data.datasets[0].data = values;
            this.charts.mood.update();
        }
    }

    createEmotionCalendar() {
        const calendar = document.getElementById('emotion-calendar');
        if (!calendar) return;

        // Create a simple calendar view
        const today = new Date();
        const daysInMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0).getDate();
        
        calendar.innerHTML = '';
        
        for (let day = 1; day <= daysInMonth; day++) {
            const dayElement = document.createElement('div');
            dayElement.className = 'calendar-day';
            dayElement.innerHTML = `
                <span class="day-number">${day}</span>
                <div class="emotion-indicator" data-emotion="neutral"></div>
            `;
            calendar.appendChild(dayElement);
        }
    }

    exportData() {
        // Export analytics data as JSON
        fetch(`${this.apiBase}/mood-analytics/default`)
            .then(response => response.json())
            .then(data => {
                const blob = new Blob([JSON.stringify(data, null, 2)], {
                    type: 'application/json'
                });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'mindwell-analytics.json';
                a.click();
                URL.revokeObjectURL(url);
            });
    }
}

// Initialize emotion chart when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.emotionChart = new EmotionChart();
});
