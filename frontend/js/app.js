// Main application controller
class MindWellApp {
    constructor() {
        this.apiBase = 'http://localhost:8000';
        this.currentSection = 'dashboard';
        this.userId = 'default';
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadDashboard();
        this.setupNavigation();
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = e.target.dataset.section;
                this.switchSection(section);
            });
        });

        // Global events
        window.addEventListener('resize', this.handleResize.bind(this));
    }

    setupNavigation() {
        // Mobile menu toggle
        const menuToggle = document.querySelector('.menu-toggle');
        if (menuToggle) {
            menuToggle.addEventListener('click', () => {
                document.querySelector('.nav-links').classList.toggle('active');
            });
        }
    }

    switchSection(sectionName) {
        // Hide all sections
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.remove('active');
        });

        // Show target section
        const targetSection = document.getElementById(sectionName);
        if (targetSection) {
            targetSection.classList.add('active');
            this.currentSection = sectionName;
            
            // Update nav active state
            document.querySelectorAll('.nav-link').forEach(link => {
                link.classList.remove('active');
            });
            document.querySelector(`[data-section="${sectionName}"]`).classList.add('active');

            // Load section-specific data
            this.loadSectionData(sectionName);
        }
    }

    loadSectionData(sectionName) {
        switch(sectionName) {
            case 'dashboard':
                this.loadDashboard();
                break;
            case 'camera':
                this.loadCameraSection();
                break;
            case 'chat':
                this.loadChatSection();
                break;
            case 'analytics':
                this.loadAnalyticsSection();
                break;
        }
    }

    async loadDashboard() {
        try {
            // Load mood analytics
            const response = await fetch(`${this.apiBase}/mood-analytics/${this.userId}`);
            const analytics = await response.json();
            
            this.updateDashboardCards(analytics);
        } catch (error) {
            console.error('Error loading dashboard:', error);
        }
    }

    updateDashboardCards(analytics) {
        // Update emotion distribution
        if (analytics.emotion_counts) {
            this.updateEmotionChart(analytics.emotion_counts);
        }

        // Update stats
        if (analytics.summary) {
            document.getElementById('total-days').textContent = analytics.summary.total_entries || 0;
            document.getElementById('positive-days').textContent = 
                Object.keys(analytics.summary.emotion_distribution || {})
                    .filter(e => ['Happy', 'Surprise'].includes(e))
                    .reduce((sum, e) => sum + (analytics.summary.emotion_distribution[e] || 0), 0);
        }

        // Update daily tip
        this.updateDailyTip();
    }

    updateEmotionChart(emotionCounts) {
        const canvas = document.getElementById('mood-chart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const labels = Object.keys(emotionCounts);
        const data = Object.values(emotionCounts);

        // Clear previous chart
        if (window.moodChart) {
            window.moodChart.destroy();
        }

        window.moodChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: [
                        '#ef4444', // Angry
                        '#8b5cf6', // Disgust
                        '#f59e0b', // Fear
                        '#10b981', // Happy
                        '#3b82f6', // Sad
                        '#f97316', // Surprise
                        '#6b7280'  // Neutral
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#f8fafc',
                            padding: 20
                        }
                    }
                }
            }
        });
    }

    updateDailyTip() {
        const tips = [
            "Take a moment to breathe deeply and appreciate three good things in your life today.",
            "Remember: progress, not perfection. Every small step counts.",
            "Your emotions are valid. Allow yourself to feel without judgment.",
            "Connect with someone you trust today - human connection is vital for wellbeing.",
            "Move your body in a way that feels good. Even a short walk can boost your mood."
        ];
        
        const tipElement = document.getElementById('daily-tip');
        if (tipElement) {
            const randomTip = tips[Math.floor(Math.random() * tips.length)];
            tipElement.querySelector('p').textContent = randomTip;
        }
    }

    loadCameraSection() {
        // Camera section will be initialized by camera.js
    }

    loadChatSection() {
        // Chat section will be initialized by chatbot.js
    }

    loadAnalyticsSection() {
        // Analytics section will be initialized by emotion-chart.js
    }

    handleResize() {
        // Handle responsive behavior
        if (window.moodChart) {
            window.moodChart.resize();
        }
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }

    async checkBackendConnection() {
        try {
            const response = await fetch(`${this.apiBase}/health`);
            const data = await response.json();
            return data.status === 'healthy';
        } catch (error) {
            console.error('Backend connection failed:', error);
            return false;
        }
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.mindWellApp = new MindWellApp();
    
    // Check backend connection
    window.mindWellApp.checkBackendConnection().then(isConnected => {
        if (!isConnected) {
            window.mindWellApp.showNotification(
                'Backend server not connected. Please start the backend server.',
                'error'
            );
        }
    });
});

// Utility functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        weekday: 'short', 
        month: 'short', 
        day: 'numeric' 
    });
}

function formatTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
}

// Export for use in other modules
window.MindWellApp = MindWellApp;
