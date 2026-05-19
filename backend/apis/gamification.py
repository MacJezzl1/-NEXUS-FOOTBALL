"""
⚽ NEXUS FOOTBALL — Gamification System
User engagement & tournament prediction game
"""

from fastapi import APIRouter, WebSocket, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# ━━━━━ DATA MODELS ━━━━━

class UserProfile(BaseModel):
    """User profile and statistics"""
    user_id: str
    username: str
    avatar_url: Optional[str]
    country: str
    total_points: int = 0
    correct_predictions: int = 0
    total_predictions: int = 0
    accuracy_percentage: float = 0.0
    tournament_rank: int = 0
    streak: int = 0

class Prediction(BaseModel):
    """User prediction submission"""
    user_id: str
    match_id: str
    predicted_winner: str
    predicted_score: str  # e.g., "2-1"
    confidence: int = 50  # 1-100

class Achievement(BaseModel):
    """User achievement/badge"""
    achievement_id: str
    name: str
    description: str
    points: int
    unlocked_at: datetime
    icon_url: str

class Leaderboard(BaseModel):
    """Tournament leaderboard entry"""
    rank: int
    user_id: str
    username: str
    total_points: int
    correct_predictions: int
    accuracy_percentage: float
    streak: int

# ━━━━━ ACHIEVEMENTS SYSTEM ━━━━━

class AchievementEngine:
    """Manage user achievements and badges"""
    
    ACHIEVEMENTS = {
        'first_prediction': {
            'name': 'First Pick',
            'description': 'Submit your first match prediction',
            'points': 10
        },
        'perfect_day': {
            'name': 'Perfect Day',
            'description': 'Get all matches correct in a single day',
            'points': 100
        },
        'streak_5': {
            'name': 'On Fire',
            'description': 'Get 5 correct predictions in a row',
            'points': 50
        },
        'streak_10': {
            'name': 'Unstoppable',
            'description': 'Get 10 correct predictions in a row',
            'points': 200
        },
        'predict_all_104': {
            'name': 'Tournament Expert',
            'description': 'Make predictions for all 104 matches',
            'points': 150
        },
        'top_10_global': {
            'name': 'Top 10 Worldwide',
            'description': 'Reach top 10 on global leaderboard',
            'points': 500
        },
        'accuracy_80': {
            'name': 'Prediction Master',
            'description': 'Achieve 80% prediction accuracy',
            'points': 300
        },
        'group_stage_perfect': {
            'name': 'Group Stage Champion',
            'description': 'Perfect predictions in group stage',
            'points': 250
        }
    }
    
    def check_achievements(self, user: UserProfile, trigger: str) -> List[Achievement]:
        """Check if user unlocked any achievements"""
        unlocked = []
        
        if trigger == 'first_prediction' and user.total_predictions == 1:
            unlocked.append(self._create_achievement('first_prediction'))
        
        if trigger == 'streak_update':
            if user.streak == 5:
                unlocked.append(self._create_achievement('streak_5'))
            elif user.streak == 10:
                unlocked.append(self._create_achievement('streak_10'))
        
        if trigger == 'accuracy_update' and user.accuracy_percentage >= 80:
            unlocked.append(self._create_achievement('accuracy_80'))
        
        return unlocked
    
    def _create_achievement(self, achievement_id: str) -> Achievement:
        """Create achievement object"""
        data = self.ACHIEVEMENTS[achievement_id]
        return Achievement(
            achievement_id=achievement_id,
            name=data['name'],
            description=data['description'],
            points=data['points'],
            unlocked_at=datetime.now(),
            icon_url=f"/badges/{achievement_id}.png"
        )

# ━━━━━ PREDICTION GAME ENGINE ━━━━━

class PredictionGameEngine:
    """Game logic and scoring"""
    
    # Point system
    CORRECT_PREDICTION = 10
    CORRECT_SCORE = 20
    CONFIDENCE_BONUS = 5  # Bonus per 10% confidence
    STREAK_MULTIPLIER = 1.1
    
    def __init__(self):
        self.achievement_engine = AchievementEngine()
        self.predictions = {}
        self.users = {}
    
    def submit_prediction(self, prediction: Prediction) -> Dict:
        """Submit a match prediction"""
        logger.info(f"Prediction from {prediction.user_id}: {prediction.match_id}")
        
        # Store prediction
        self.predictions[f"{prediction.user_id}_{prediction.match_id}"] = prediction
        
        # Initialize user if not exists
        if prediction.user_id not in self.users:
            self.users[prediction.user_id] = UserProfile(
                user_id=prediction.user_id,
                username=f"Player_{prediction.user_id[:8]}"
            )
        
        user = self.users[prediction.user_id]
        user.total_predictions += 1
        
        # Check for achievements
        achievements = self.achievement_engine.check_achievements(user, 'first_prediction')
        
        return {
            'status': 'success',
            'message': 'Prediction submitted',
            'achievements_unlocked': achievements
        }
    
    def evaluate_prediction(self, match_id: str, actual_score: str) -> None:
        """Evaluate all predictions for a match"""
        logger.info(f"Evaluating predictions for match {match_id}: {actual_score}")
        
        for pred_key, prediction in self.predictions.items():
            if match_id not in pred_key:
                continue
            
            user = self.users[prediction.user_id]
            is_correct = prediction.predicted_score == actual_score
            
            if is_correct:
                user.correct_predictions += 1
                points = self.CORRECT_SCORE
                
                # Add confidence bonus
                confidence_multiplier = 1 + (prediction.confidence / 100) * self.CONFIDENCE_BONUS
                points = int(points * confidence_multiplier)
                
                # Add streak multiplier
                user.streak += 1
                if user.streak > 1:
                    points = int(points * (self.STREAK_MULTIPLIER ** (user.streak - 1)))
                
                user.total_points += points
            else:
                user.streak = 0
            
            # Update accuracy
            user.accuracy_percentage = (user.correct_predictions / user.total_predictions) * 100
            
            # Check for achievements
            achievements = self.achievement_engine.check_achievements(user, 'accuracy_update')
            if user.streak >= 5:
                achievements.extend(
                    self.achievement_engine.check_achievements(user, 'streak_update')
                )
    
    def get_leaderboard(self, limit: int = 100) -> List[Leaderboard]:
        """Get global leaderboard"""
        sorted_users = sorted(
            self.users.values(),
            key=lambda u: u.total_points,
            reverse=True
        )
        
        leaderboard = []
        for rank, user in enumerate(sorted_users[:limit], 1):
            leaderboard.append(Leaderboard(
                rank=rank,
                user_id=user.user_id,
                username=user.username,
                total_points=user.total_points,
                correct_predictions=user.correct_predictions,
                accuracy_percentage=user.accuracy_percentage,
                streak=user.streak
            ))
        
        return leaderboard

# ━━━━━ WEBSOCKET REAL-TIME UPDATES ━━━━━

class ConnectionManager:
    """Manage WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"User {user_id} connected")
    
    async def disconnect(self, user_id: str):
        """Remove WebSocket connection"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            logger.info(f"User {user_id} disconnected")
    
    async def broadcast_prediction_result(self, match_id: str, result: Dict):
        """Broadcast prediction results to all connected users"""
        for user_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json({
                    'type': 'prediction_result',
                    'match_id': match_id,
                    'result': result
                })
            except Exception as e:
                logger.error(f"Error sending to {user_id}: {str(e)}")
    
    async def send_personal_achievement(self, user_id: str, achievement: Achievement):
        """Send achievement notification to specific user"""
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json({
                'type': 'achievement_unlocked',
                'achievement': achievement.dict()
            })

# ━━━━━ GLOBAL INSTANCES ━━━━━

game_engine = PredictionGameEngine()
manager = ConnectionManager()

# ━━━━━ API ENDPOINTS ━━━━━

@router.post("/predict", tags=["Gamification"])
async def submit_prediction(prediction: Prediction):
    """Submit a match prediction"""
    try:
        result = game_engine.submit_prediction(prediction)
        return result
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/leaderboard", response_model=List[Leaderboard], tags=["Gamification"])
async def get_leaderboard(limit: int = Query(100, le=1000)):
    """Get tournament leaderboard"""
    return game_engine.get_leaderboard(limit)

@router.get("/user/{user_id}/profile", response_model=UserProfile, tags=["Gamification"])
async def get_user_profile(user_id: str):
    """Get user profile and stats"""
    if user_id not in game_engine.users:
        raise HTTPException(status_code=404, detail="User not found")
    
    return game_engine.users[user_id]

@router.get("/user/{user_id}/achievements", response_model=List[Achievement], tags=["Gamification"])
async def get_user_achievements(user_id: str):
    """Get user's unlocked achievements"""
    # TODO: Query from database
    return []

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket for real-time updates"""
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get('type') == 'prediction':
                prediction = Prediction(**data['payload'])
                result = game_engine.submit_prediction(prediction)
                await websocket.send_json(result)
    
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        await manager.disconnect(user_id)
