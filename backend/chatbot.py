import json
import random
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class WellnessChatbot:
    def __init__(self):
        self.conversation_history = {}
        self.emotion_responses = self.load_emotion_responses()
        self.wellness_tips = self.load_wellness_tips()
        self.meditation_guides = self.load_meditation_guides()
        
    def load_emotion_responses(self):
        """Load predefined responses for different emotions"""
        return {
            'Happy': {
                'responses': [
                    "It's wonderful to see you happy! Keep nurturing this positive energy.",
                    "Your happiness is contagious! What made you feel this way today?",
                    "Embrace this joy - it's a powerful emotion that boosts your wellbeing."
                ],
                'recommendations': [
                    "Share your happiness with others - it multiplies!",
                    "Practice gratitude journaling to maintain this positive state",
                    "Listen to upbeat music to amplify your mood"
                ]
            },
            'Sad': {
                'responses': [
                    "I'm here for you. It's okay to feel sad - emotions are temporary visitors.",
                    "Your feelings are valid. Would you like to talk about what's on your mind?",
                    "Sadness is a natural part of life. Let's work through this together."
                ],
                'recommendations': [
                    "Try a 5-minute breathing exercise to center yourself",
                    "Reach out to a friend or loved one - connection helps",
                    "Listen to gentle, uplifting music or nature sounds",
                    "Take a short walk outside - movement can shift your mood"
                ]
            },
            'Angry': {
                'responses': [
                    "I sense you're feeling angry. Let's find healthy ways to process this.",
                    "Anger often signals that something important needs attention.",
                    "Your anger is valid. Let's channel it constructively."
                ],
                'recommendations': [
                    "Try progressive muscle relaxation to release tension",
                    "Write down what's bothering you - it helps process emotions",
                    "Take 10 deep breaths, counting to 4 on each inhale and exhale",
                    "Listen to calming instrumental music"
                ]
            },
            'Fear': {
                'responses': [
                    "Feeling fear is completely natural. You're safe right now.",
                    "Fear often shows us what we care about deeply.",
                    "Let's work together to find your inner strength."
                ],
                'recommendations': [
                    "Practice grounding: name 5 things you can see, 4 you can touch...",
                    "Try a short guided meditation for anxiety relief",
                    "Listen to calming nature sounds or gentle music",
                    "Remember past times you've overcome challenges"
                ]
            },
            'Surprise': {
                'responses': [
                    "What a surprise! How are you feeling about this unexpected moment?",
                    "Surprises can be exciting or overwhelming - both are okay.",
                    "This surprise has shifted your energy - notice how you feel."
                ],
                'recommendations': [
                    "Take a moment to process this surprise mindfully",
                    "Share this moment with someone you trust",
                    "Write about this experience to capture your feelings"
                ]
            },
            'Neutral': {
                'responses': [
                    "I see you're in a calm, neutral state. This is a good baseline for mindfulness.",
                    "Neutral emotions are perfect moments for self-reflection.",
                    "How are you feeling in this moment of calm?"
                ],
                'recommendations': [
                    "Try a brief mindfulness meditation",
                    "Practice gratitude by noticing three good things",
                    "Take a moment to check in with your body and breath"
                ]
            }
        }
    
    def load_wellness_tips(self):
        """Load general wellness tips"""
        return [
            "Remember to drink water regularly - hydration affects mood!",
            "Take short breaks every hour to stretch and breathe",
            "Connect with nature daily, even if just looking out a window",
            "Practice self-compassion - treat yourself as you would a good friend",
            "Get adequate sleep - it's crucial for emotional regulation",
            "Limit social media if it's affecting your mood negatively",
            "Practice saying no to protect your energy",
            "Celebrate small wins throughout your day"
        ]
    
    def load_meditation_guides(self):
        """Load meditation and breathing exercises"""
        return {
            'breathing_5min': {
                'title': '5-Minute Calming Breath',
                'steps': [
                    "Find a comfortable position and close your eyes",
                    "Inhale slowly for 4 counts",
                    "Hold your breath gently for 4 counts",
                    "Exhale slowly for 6 counts",
                    "Repeat this cycle for 5 minutes",
                    "Notice how your body feels more relaxed"
                ]
            },
            'body_scan': {
                'title': 'Quick Body Scan',
                'steps': [
                    "Start at the top of your head",
                    "Slowly scan down through your body",
                    "Notice any tension without trying to change it",
                    "Breathe into areas of tightness",
                    "Allow your whole body to relax"
                ]
            },
            'gratitude_meditation': {
                'title': 'Gratitude Reflection',
                'steps': [
                    "Think of three things you're grateful for today",
                    "Focus on each one for 30 seconds",
                    "Notice how gratitude feels in your body",
                    "Let this feeling expand throughout your being"
                ]
            }
        }
    
    def get_response(self, message, user_id="default"):
        """Generate AI response based on user message"""
        message_lower = message.lower()
        
        # Initialize conversation history for new users
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        # Add user message to history
        self.conversation_history[user_id].append({
            "role": "user",
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Check for specific keywords
        response = self.process_message(message_lower, user_id)
        
        # Add bot response to history
        self.conversation_history[user_id].append({
            "role": "bot",
            "message": response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only last 10 messages
        self.conversation_history[user_id] = self.conversation_history[user_id][-10:]
        
        return response
    
    def process_message(self, message, user_id):
        """Process message and generate appropriate response"""
        
        # Check for meditation requests
        if any(word in message for word in ['meditation', 'breathe', 'calm', 'relax']):
            return self.get_meditation_guide()
        
        # Check for wellness tips
        if any(word in message for word in ['tip', 'advice', 'help', 'suggestion']):
            return random.choice(self.wellness_tips)
        
        # Check for mood/emotion keywords
        emotion_keywords = {
            'happy': 'Happy', 'joy': 'Happy', 'excited': 'Happy',
            'sad': 'Sad', 'down': 'Sad', 'depressed': 'Sad',
            'angry': 'Angry', 'mad': 'Angry', 'frustrated': 'Angry',
            'scared': 'Fear', 'anxious': 'Fear', 'worried': 'Fear',
            'surprised': 'Surprise',
