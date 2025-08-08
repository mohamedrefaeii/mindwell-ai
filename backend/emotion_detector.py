import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPooling2D
from tensorflow.keras.optimizers import Adam
import os
import logging

logger = logging.getLogger(__name__)

class EmotionDetector:
    def __init__(self):
        self.emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Load pre-trained emotion detection model or create a new one"""
        model_path = 'models/emotion_model.h5'
        
        if os.path.exists(model_path):
            try:
                self.model = tf.keras.models.load_model(model_path)
                logger.info("Loaded pre-trained emotion model")
            except Exception as e:
                logger.error(f"Error loading model: {e}")
                self.create_model()
        else:
            logger.info("Creating new emotion model")
            self.create_model()
    
    def create_model(self):
        """Create and compile emotion detection model"""
        self.model = Sequential([
            Conv2D(32, (3, 3), activation='relu', input_shape=(48, 48, 1)),
            Conv2D(64, (3, 3), activation='relu'),
            MaxPooling2D(pool_size=(2, 2)),
            Dropout(0.25),
            
            Conv2D(128, (3, 3), activation='relu'),
            MaxPooling2D(pool_size=(2, 2)),
            Conv2D(128, (3, 3), activation='relu'),
            MaxPooling2D(pool_size=(2, 2)),
            Dropout(0.25),
            
            Flatten(),
            Dense(1024, activation='relu'),
            Dropout(0.5),
            Dense(7, activation='softmax')
        ])
        
        self.model.compile(
            loss='categorical_crossentropy',
            optimizer=Adam(learning_rate=0.0001),
            metrics=['accuracy']
        )
        
        # Create models directory if it doesn't exist
        os.makedirs('models', exist_ok=True)
        
        # Save the initial model
        self.model.save('models/emotion_model.h5')
        logger.info("Created and saved new emotion model")
    
    def preprocess_face(self, face_image):
        """Preprocess face image for emotion detection"""
        # Resize to 48x48
        face_image = cv2.resize(face_image, (48, 48))
        
        # Convert to grayscale if needed
        if len(face_image.shape) == 3:
            face_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
        
        # Normalize pixel values
        face_image = face_image.astype('float32') / 255.0
        
        # Reshape for model input
        face_image = face_image.reshape(1, 48, 48, 1)
        
        return face_image
    
    def predict_emotion(self, frame):
        """Predict emotion from frame"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            if len(faces) > 0:
                # Get the largest face
                largest_face = max(faces, key=lambda x: x[2] * x[3])
                x, y, w, h = largest_face
                
                # Extract face region
                face_roi = gray[y:y+h, x:x+w]
                
                # Preprocess face
                processed_face = self.preprocess_face(face_roi)
                
                # Predict emotion
                predictions = self.model.predict(processed_face)
                emotion_index = np.argmax(predictions[0])
                confidence = predictions[0][emotion_index]
                
                emotion = self.emotion_labels[emotion_index]
                
                return emotion, float(confidence)
            else:
                return "No Face", 0.0
                
        except Exception as e:
            logger.error(f"Error in emotion prediction: {e}")
            return "Error", 0.0
    
    def get_emotion_color(self, emotion):
        """Get color associated with emotion for visualization"""
        color_map = {
            'Angry': (255, 0, 0),      # Red
            'Disgust': (128, 0, 128),  # Purple
            'Fear': (0, 0, 139),       # Dark Blue
            'Happy': (255, 255, 0),    # Yellow
            'Sad': (0, 0, 255),        # Blue
            'Surprise': (255, 165, 0), # Orange
            'Neutral': (128, 128, 128) # Gray
        }
        return color_map.get(emotion, (255, 255, 255))
    
    def draw_emotion_info(self, frame, emotion, confidence):
        """Draw emotion information on frame"""
        if emotion != "No Face" and emotion != "Error":
            color = self.get_emotion_color(emotion)
            
            # Draw background rectangle
            cv2.rectangle(frame, (0, 0), (300, 80), (0, 0, 0), -1)
            
            # Draw emotion text
            cv2.putText(frame, f"Emotion: {emotion}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            
            # Draw confidence
            cv2.putText(frame, f"Confidence: {confidence:.2f}", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        return frame
