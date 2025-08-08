import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Any
import os

logger = logging.getLogger(__name__)

class MoodAnalytics:
    def __init__(self):
        self.data_file = 'data/mood_entries.json'
        self.ensure_data_directory()
        self.load_data()
    
    def ensure_data_directory(self):
        """Ensure data directory exists"""
        os.makedirs('data', exist_ok=True)
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w') as f:
                json.dump([], f)
    
    def load_data(self):
        """Load mood entry data"""
        try:
            with open(self.data_file, 'r') as f:
                self.data = json.load(f)
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            self.data = []
    
    def save_data(self):
        """Save mood entry data"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving data: {e}")
    
    def save_entry(self, entry: Dict[str, Any]):
        """Save a new mood entry"""
        entry['id'] = len(self.data) + 1
        entry['timestamp'] = entry.get('timestamp', datetime.now().isoformat())
        self.data.append(entry)
        self.save_data()
    
    def get_user_analytics(self, user_id: str = "default") -> Dict[str, Any]:
        """Get comprehensive analytics for a user"""
        user_data = [entry for entry in self.data if entry.get('user_id', 'default') == user_id]
        
        if not user_data:
            return self.get_empty_analytics()
        
        df = pd.DataFrame(user_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Basic statistics
        total_entries = len(user_data)
        emotion_counts = df['emotion'].value_counts().to_dict()
        
        # Time-based analytics
        last_7_days = df[df['timestamp'] >= datetime.now() - timedelta(days=7)]
        last_30_days = df[df['timestamp'] >= datetime.now() - timedelta(days=30)]
        
        # Mood trends
        mood_trends = self.calculate_mood_trends(df)
        
        # Emotional patterns
        patterns = self.analyze_patterns(df)
        
        # Recommendations
        recommendations = self.generate_recommendations(df)
        
        return {
            'summary': {
                'total_entries': total_entries,
                'date_range': {
                    'start': df['timestamp'].min().isoformat(),
                    'end': df['timestamp'].max().isoformat()
                },
                'most_common_emotion': max(emotion_counts.items(), key=lambda x: x[1])[0] if emotion_counts else None,
                'emotion_distribution': emotion_counts
            },
            'trends': mood_trends,
            'patterns': patterns,
            'recommendations': recommendations,
            'recent_entries': user_data[-5:] if len(user_data) > 5 else user_data
        }
    
    def calculate_mood_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate mood trends over time"""
        if len(df) < 2:
            return {'message': 'Not enough data for trends'}
        
        # Create emotion scores (positive emotions = higher score)
        emotion_scores = {
            'Happy': 5, 'Surprise': 4, 'Neutral': 3,
            'Sad': 2, 'Fear': 1, 'Angry': 1, 'Disgust': 1
        }
        
        df['emotion_score'] = df['emotion'].map(emotion_scores)
        
        # Daily trends
        daily_trends = df.groupby(df['timestamp'].dt.date)['emotion_score'].mean().to_dict()
        
        # Weekly trends
        weekly_trends = df.groupby(df['timestamp'].dt.isocalendar().week)['emotion_score'].mean().to_dict()
        
        # Calculate trend direction
        if len(daily_trends) > 1:
            recent_scores = list(daily_trends.values())[-7:]
            if len(recent_scores) > 1:
                trend_direction = 'improving' if recent_scores[-1] > recent_scores[0] else 'declining'
            else:
                trend_direction = 'stable'
        else:
            trend_direction = 'insufficient_data'
        
        return {
            'daily_trends': {str(k): v for k, v in daily_trends.items()},
            'weekly_trends': {str(k): v for k, v in weekly_trends.items()},
            'trend_direction': trend_direction,
            'average_score': float(df['emotion_score'].mean()),
            'score_std': float(df['emotion_score'].std())
        }
    
    def analyze_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze emotional patterns"""
        if len(df) < 3:
            return {'message': 'Not enough data for pattern analysis'}
        
        # Time of day patterns
        df['hour'] = df['timestamp'].dt.hour
        hourly_patterns = df.groupby('hour')['emotion'].agg(lambda x: x.mode()[0] if len(x) > 0 else 'Neutral').to_dict()
        
        # Day of week patterns
        df['day_of_week'] = df['timestamp'].dt.day_name()
        daily_patterns = df.groupby('day_of_week')['emotion'].agg(lambda x: x.mode()[0] if len(x) > 0 else 'Neutral').to_dict()
        
        # Emotional triggers (based on notes)
        notes_analysis = self.analyze_notes(df)
        
        # Mood stability
        emotion_changes = df['emotion'].ne(df['emotion'].shift()).sum()
        stability_score = 1 - (emotion_changes / len(df))
        
        return {
            'hourly_patterns': hourly_patterns,
            'daily_patterns': daily_patterns,
            'mood_stability': float(stability_score),
            'notes_analysis': notes_analysis,
            'emotional_variety': len(df['emotion'].unique())
        }
    
    def analyze_notes(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze notes for emotional triggers"""
        if 'notes' not in df.columns or df['notes'].isna().all():
            return {'message': 'No notes available for analysis'}
        
        notes_df = df[df['notes'].notna()]
        if len(notes_df) == 0:
            return {'message': 'No valid notes for analysis'}
        
        # Simple keyword analysis
        keywords = {
            'work': ['work', 'job', 'office', 'meeting', 'project'],
            'relationship': ['friend', 'family', 'love', 'partner', 'relationship'],
            'health': ['tired', 'sick', 'pain', 'exercise', 'sleep'],
            'stress': ['stress', 'anxious', 'worried', 'overwhelmed', 'pressure']
        }
        
        keyword_matches = {}
        for category, words in keywords.items():
            matches = notes_df['notes'].str.contains('|'.join(words), case=False, na=False).sum()
            keyword_matches[category] = int(matches)
        
        # Emotion-note correlation
        emotion_note_pairs = notes_df.groupby('emotion')['notes'].count().to_dict()
        
        return {
            'keyword_matches': keyword_matches,
            'emotion_note_correlation': emotion_note_pairs,
            'total_notes_analyzed': len(notes_df)
        }
    
    def generate_recommendations(self, df: pd.DataFrame) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        emotion_counts = df['emotion'].value_counts()
        
        # Based on most common emotion
        if not emotion_counts.empty:
            most_common = emotion_counts.index[0]
            
            if most_common in ['Sad', 'Angry', 'Fear']:
                recommendations.extend([
                    "Consider daily mindfulness practice for emotional regulation",
                    "Try journaling your feelings to process<create_file>
<path>mindwell-ai/backend/mood_analytics.py</path>
<content>
import pandas as pd
import os
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MoodAnalytics:
    def __init__(self):
        self.data_file = 'mood_data.json'
        self.data = []
        self.load_data()
    
    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.data = json.load(f)
                logger.info("Loaded mood data")
            except Exception as e:
                logger.error(f"Error loading mood data: {e}")
                self.data = []
        else:
            self.data = []
    
    def save_data(self):
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=4)
            logger.info("Saved mood data")
        except Exception as e:
            logger.error(f"Error saving mood data: {e}")
    
    def save_entry(self, entry):
        """Save a new mood entry"""
        self.data.append(entry)
        self.save_data()
    
    def get_user_analytics(self, user_id):
        """Return analytics for a user"""
        # For now, user_id is not used, but can be extended
        if not self.data:
            return {"message": "No mood data available"}
        
        df = pd.DataFrame(self.data)
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Basic stats
        emotion_counts = df['emotion'].value_counts().to_dict()
        avg_intensity = df['intensity'].mean() if 'intensity' in df.columns else None
        
        # Time series data for mood tracking
        time_series = df.groupby(df['timestamp'].dt.date)['intensity'].mean().fillna(0).to_dict()
        
        analytics = {
            "emotion_counts": emotion_counts,
            "average_intensity": avg_intensity,
            "time_series": time_series
        }
        
        return analytics
