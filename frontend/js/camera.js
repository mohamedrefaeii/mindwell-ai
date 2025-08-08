// Real-time camera and emotion detection
class CameraManager {
    constructor() {
        this.video = document.getElementById('video');
        this.canvas = document.getElementById('overlay');
        this.ctx = this.canvas.getContext('2d');
        this.stream = null;
        this.ws = null;
        this.isStreaming = false;
        this.detectedEmotions = [];
        
        this.init();
    }

    init() {
        this.setupCanvas();
        this.setupWebSocket();
        this.setupControls();
    }

    setupCanvas() {
        this.canvas.width = 640;
        this.canvas.height = 480;
    }

    setupWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        this.ws = new WebSocket(`${protocol}//localhost:8000/ws/emotion-stream`);
        
        this.ws.onopen = () => {
            console.log('WebSocket connected for emotion streaming');
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleEmotionData(data);
        };
        
        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }

    setupControls() {
        const startBtn = document.getElementById('start-camera');
        const stopBtn = document.getElementById('stop-camera');
        const captureBtn = document.getElementById('capture-mood');

        if (startBtn) startBtn.addEventListener('click', () => this.startCamera());
        if (stopBtn) stopBtn.addEventListener('click', () => this.stopCamera());
        if (captureBtn) captureBtn.addEventListener('click', () => this.captureMood());
    }

    async startCamera() {
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: { width: 640, height: 480 },
                audio: false
            });
            
            this.video.srcObject = this.stream;
            this.isStreaming = true;
            
            // Start emotion detection
            this.startEmotionDetection();
            
            // Update UI
            this.updateCameraUI('started');
            
        } catch (error) {
            console.error('Error accessing camera:', error);
            this.showCameraError('Unable to access camera. Please check permissions.');
        }
    }

    stopCamera() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
            this.isStreaming = false;
        }
        
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.close();
        }
        
        this.updateCameraUI('stopped');
    }

    startEmotionDetection() {
        const sendFrame = () => {
            if (!this.isStreaming || !this.ws || this.ws.readyState !== WebSocket.OPEN) {
                return;
            }

            // Create a temporary canvas to capture the video frame
            const tempCanvas = document.createElement('canvas');
            tempCanvas.width = 640;
            tempCanvas.height = 480;
            const tempCtx = tempCanvas.getContext('2d');
            tempCtx.drawImage(this.video, 0, 0, 640, 480);

            // Convert to base64
            const imageData = tempCanvas.toDataURL('image/jpeg', 0.8);
            
            // Send to backend
            this.ws.send(JSON.stringify({
                type: 'frame',
                data: imageData
            }));

            // Continue sending frames
            setTimeout(sendFrame, 100); // 10 FPS
        };

        sendFrame();
    }

    handleEmotionData(data) {
        const { emotion, confidence } = data;
        
        // Update emotion display
        this.updateEmotionDisplay(emotion, confidence);
        
        // Store emotion for analytics
        this.storeEmotion(emotion, confidence);
        
        // Update recommendations
        this.updateRecommendations(emotion);
        
        // Visual feedback
        this.addEmotionAnimation(emotion);
    }

    updateEmotionDisplay(emotion, confidence) {
        const emotionElement = document.getElementById('detected-emotion');
        const confidenceElement = document.getElementById('confidence');
        
        if (emotionElement) {
            emotionElement.textContent = emotion;
            emotionElement.className = `emotion-${emotion.toLowerCase()}`;
        }
        
        if (confidenceElement) {
            confidenceElement.textContent = `${Math.round(confidence * 100)}%`;
        }

        // Update emotion icon
        const iconElement = document.querySelector('.emotion-icon i');
        if (iconElement) {
            const iconMap = {
                'Happy': 'fas fa-smile',
                'Sad': 'fas fa-sad-tear',
                'Angry': 'fas fa-angry',
                'Fear': 'fas fa-frown',
                'Surprise': 'fas fa-surprise',
                'Neutral': 'fas fa-meh',
                'Disgust': 'fas fa-dizzy'
            };
            
            iconElement.className = iconMap[emotion] || 'fas fa-question';
        }
    }

    storeEmotion(emotion, confidence) {
        const timestamp = new Date().toISOString();
        this.detectedEmotions.push({ emotion, confidence, timestamp });
        
        // Keep only last 100 emotions
        if (this.detectedEmotions.length > 100) {
            this.detectedEmotions.shift();
        }
        
        // Update today's emotions display
        this.updateTodayEmotions();
    }

    updateTodayEmotions() {
        const today = new Date().toDateString();
        const todayEmotions = this.detectedEmotions.filter(e => 
            new Date(e.timestamp).toDateString() === today
        );
        
        const emotionCounts = {};
        todayEmotions.forEach(e => {
            emotionCounts[e.emotion] = (emotionCounts[e.emotion] || 0) + 1;
        });
        
        const container = document.getElementById('today-emotions');
        if (container) {
            container.innerHTML = '';
            
            Object.entries(emotionCounts).forEach(([emotion, count]) => {
                const emotionDiv = document.createElement('div');
                emotionDiv.className = 'emotion-item';
                emotionDiv.innerHTML = `
                    <span class="emotion-name">${emotion}</span>
                    <span class="emotion-count">${count}</span>
                `;
                container.appendChild(emotionDiv);
            });
        }
    }

    async updateRecommendations(emotion) {
        try {
            const response = await fetch(`http://localhost:8000/recommendations/${emotion}`);
            const data = await response.json();
            
            const container = document.getElementById('emotion-recommendations');
            if (container && data.recommendations) {
                container.innerHTML = '';
                
                data.recommendations.forEach(rec => {
                    const recDiv = document.createElement('div');
                    recDiv.className = 'recommendation-item';
                    recDiv.innerHTML = `
                        <i class="fas fa-lightbulb"></i>
                        <span>${rec}</span>
                    `;
                    container.appendChild(recDiv);
                });
            }
        } catch (error) {
            console.error('Error loading recommendations:', error);
        }
    }

    addEmotionAnimation(emotion) {
        const container = document.querySelector('.camera-preview');
        if (!container) return;
        
        const animation = document.createElement('div');
        animation.className = 'emotion-animation';
        animation.style.cssText = `
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 3rem;
            animation: emotionPop 1s ease-out forwards;
            pointer-events: none;
            z-index: 1000;
        `;
        
        const emojiMap = {
            'Happy': '😊',
            'Sad': '😢',
            'Angry': '😠',
            'Fear': '😨',
            'Surprise': '😮',
            'Neutral': '😐',
            'Disgust': '🤢'
        };
        
        animation.textContent = emojiMap[emotion] || '❓';
        container.appendChild(animation);
        
        // Remove animation after it completes
        setTimeout(() => {
            if (animation.parentNode) {
                animation.parentNode.removeChild(animation);
            }
        }, 1000);
    }

    async captureMood() {
        if (!this.isStreaming) {
            this.showCameraError('Please start the camera first');
            return;
        }

        try {
            // Create canvas to capture current frame
            const canvas = document.createElement('canvas');
            canvas.width = 640;
            canvas.height = 480;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(this.video, 0, 0, 640, 480);

            // Convert to blob
            canvas.toBlob(async (blob) => {
                const formData = new FormData();
                formData.append('file', blob, 'emotion.jpg');

                const response = await fetch('http://localhost:8000/analyze-emotion', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();
                
                // Save mood entry
                await this.saveMoodEntry(data.emotion, data.confidence);
                
                // Show success message
                this.showNotification(`Mood captured: ${data.emotion} (${Math.round(data.confidence * 100)}% confidence)`);
            }, 'image/jpeg', 0.9);
            
        } catch (error) {
            console.error('Error capturing mood:', error);
            this.showCameraError('Error capturing mood. Please try again.');
        }
    }

    async saveMoodEntry(emotion, confidence) {
        try {
            const response = await fetch('http://localhost:8000/mood-entry', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    emotion: emotion,
                    intensity: Math.round(confidence * 100),
                    notes: `Captured via camera at ${new Date().toLocaleTimeString()}`,
                    timestamp: new Date().toISOString()
                })
            });

            if (response.ok) {
                // Refresh dashboard if it's open
                if (window.mindWellApp && window.mindWellApp.currentSection === 'dashboard') {
                    window.mindWellApp.loadDashboard();
                }
            }
        } catch (error) {
            console.error('Error saving mood entry:', error);
        }
    }

    updateCameraUI(state) {
        const startBtn = document.getElementById('start-camera');
        const stopBtn = document.getElementById('stop-camera');
        const captureBtn = document.getElementById('capture-mood');

        if (state === 'started') {
            if (startBtn) startBtn.disabled = true;
            if (stopBtn) stopBtn.disabled = false;
            if (captureBtn) captureBtn.disabled = false;
        } else {
            if (startBtn) startBtn.disabled = false;
            if (stopBtn) stopBtn.disabled = true;
            if (captureBtn) captureBtn.disabled = true;
        }
    }

    showCameraError(message) {
        const notification = document.createElement('div');
        notification.className = 'camera-error';
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #ef4444;
            color: white;
            padding: 1rem;
            border-radius: 0.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            z-index: 1000;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }

    showNotification(message) {
        if (window.mindWellApp) {
            window.mindWellApp.showNotification(message, 'success');
        }
    }
}

// Initialize camera manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.cameraManager = new CameraManager();
});

// Add CSS for emotion animations
const style = document.createElement('style');
style.textContent = `
    @keyframes emotionPop {
        0% {
            transform: translate(-50%, -50%) scale(0);
            opacity: 1;
        }
        50% {
            transform: translate(-50%, -50%) scale(1.2);
            opacity: 0.8;
        }
        100% {
            transform: translate(-50%, -50%) scale(1);
            opacity: 0;
        }
    }
    
    .emotion-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem;
        margin: 0.25rem 0;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 0.25rem;
    }
    
    .recommendation-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem;
        margin: 0.25rem 0;
        background: rgba(99, 102, 241, 0.1);
        border-radius: 0.25rem;
    }
`;
document.head.appendChild(style);
