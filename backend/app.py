from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import cv2
import numpy as np
import base64
import json
import asyncio
from datetime import datetime
import logging

from emotion_detector import EmotionDetector
from chatbot import WellnessChatbot
from mood_analytics import MoodAnalytics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="MindWell AI", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI components
emotion_detector = EmotionDetector()
chatbot = WellnessChatbot()
mood_analytics = MoodAnalytics()

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    user_id: str = "default"

class EmotionData(BaseModel):
    emotion: str
    confidence: float
    timestamp: str

class MoodEntry(BaseModel):
    emotion: str
    intensity: int
    notes: str = ""
    timestamp: str = None

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("New WebSocket connection established")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info("WebSocket connection closed")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

@app.get("/")
async def root():
    return {"message": "MindWell AI Backend - Mental Wellness Companion API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/analyze-emotion")
async def analyze_emotion(file: UploadFile = File(...)):
    """Analyze emotion from uploaded image"""
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        emotion, confidence = emotion_detector.predict_emotion(image)
        
        return {
            "emotion": emotion,
            "confidence": float(confidence),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error analyzing emotion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mood-entry")
async def save_mood_entry(entry: MoodEntry):
    """Save mood entry for analytics"""
    try:
        if entry.timestamp is None:
            entry.timestamp = datetime.now().isoformat()
        
        mood_analytics.save_entry(entry.dict())
        return {"status": "success", "message": "Mood entry saved"}
    except Exception as e:
        logger.error(f"Error saving mood entry: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/mood-analytics/{user_id}")
async def get_mood_analytics(user_id: str):
    """Get mood analytics for user"""
    try:
        analytics = mood_analytics.get_user_analytics(user_id)
        return analytics
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat_with_bot(chat_message: ChatMessage):
    """Chat with AI wellness assistant"""
    try:
        response = chatbot.get_response(chat_message.message, chat_message.user_id)
        return {
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/emotion-stream")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time emotion detection"""
    await manager.connect(websocket)
    try:
        while True:
            # Receive base64 encoded image
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "frame":
                # Decode base64 image
                image_data = base64.b64decode(message["data"].split(',')[1])
                nparr = np.frombuffer(image_data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if frame is not None:
                    # Detect emotion
                    emotion, confidence = emotion_detector.predict_emotion(frame)
                    
                    # Send back emotion data
                    response = {
                        "type": "emotion",
                        "emotion": emotion,
                        "confidence": float(confidence),
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    await websocket.send_text(json.dumps(response))
                    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.close()

@app.get("/recommendations/{emotion}")
async def get_recommendations(emotion: str):
    """Get personalized recommendations based on emotion"""
    try:
        recommendations = chatbot.get_emotion_recommendations(emotion)
        return {"recommendations": recommendations}
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
