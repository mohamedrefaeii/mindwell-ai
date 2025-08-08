# MindWell AI - Mental Wellness Companion

MindWell AI is a full-stack AI-powered web application designed to support mental wellness through real-time emotion recognition, personalized AI chatbot assistance, mood tracking, and analytics.

---

## Features

- Real-time emotion detection using your webcam with computer vision.
- AI-powered wellness chatbot for personalized mental health support.
- Mood tracking dashboard with interactive charts and analytics.
- Personalized recommendations based on detected emotions.
- Responsive and modern UI with animations and interactive elements.

---

## Technology Stack

- **Frontend:** HTML, CSS, JavaScript (with Chart.js for analytics)
- **Backend:** Python FastAPI
- **AI Models:** TensorFlow/Keras for emotion detection, custom chatbot logic
- **Real-time:** WebSocket for live emotion streaming

---

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js and npm (optional, for serving frontend)
- Webcam-enabled device and modern browser

### Backend Setup

1. Navigate to the backend directory:

```bash
cd mindwell-ai/backend
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the backend server:

```bash
uvicorn app:app --reload
```

The backend server will start at `http://localhost:8000`.

---

### Frontend Setup

1. Navigate to the frontend directory:

```bash
cd mindwell-ai/frontend
```

2. You can open `index.html` directly in your browser or serve it using a simple HTTP server:

```bash
# Using Python 3
python -m http.server 8080
```

3. Open your browser and go to `http://localhost:8080` (or open `index.html` directly).

---

## Usage

- Use the **Emotion Scan** tab to start your webcam and see real-time emotion detection.
- Chat with the AI wellness assistant in the **AI Chat** tab for personalized support.
- Track your mood and view analytics in the **Analytics** tab.
- Log moods manually or capture moods via the camera.

---

## AI Integration Explanation

- **Emotion Detection:** Uses a convolutional neural network (CNN) trained on facial expressions to classify emotions from webcam images.
- **Chatbot:** A rule-based AI assistant providing wellness tips, meditation guides, and emotional support based on user input.
- **Real-time Processing:** WebSocket connection streams webcam frames to the backend for live emotion analysis.
- **Mood Analytics:** Stores mood entries and provides visual insights using charts.

---




---

## Contact

For questions or contributions, please contact mohameddrefaee6@gmail
