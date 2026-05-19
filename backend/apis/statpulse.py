"""
🟢 StatPulse — Player Performance Rating System
"Every player. Every match. Ranked."

Scores every outfield player using composite rating system.
Position-aware: GK/DEF/MID/FWD each have specific weights.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum
import logging
import numpy as np

logger = logging.getLogger(__name__)
router = APIRouter()

# ━━━━━ ENUMS ━━━━━

class PlayerPosition(str, Enum):
    GK = "goalkeeper"
    DEF = "defender"
    MID = "midfielder"
    FWD = "forward"


# ━━━━━ DATA MODELS ━━━━━

class PlayerStats(BaseModel):
    """Individual match player statistics"""
    player_id: str
    player_name: str
    team: str
    position: PlayerPosition
    minutes_played: int
    goals: int = 0
    assists: int = 0
    xg: float = 0.0
    xa: float = 0.0
    progressive_passes: int = 0
    duels_won_pct: float = 0.0
    touches_in_box: int = 0
    errors_leading_to_shot: int = 0


class PlayerRating(BaseModel):
    """Player rating output"""
    player_id: str
    player_name: str
    team: str
    position: PlayerPosition
    match_rating: float  # 0-10 scale
    rating_per90: float
    components: Dict[str, float]  # Breakdown of rating components
    timestamp: datetime


class TournamentRanking(BaseModel):
    """Player tournament ranking"""
    rank: int
    player_name: str
    team: str
    position: PlayerPosition
    tournament_avg_rating: float
    matches_played: int
    total_goals: int
    total_assists: int


# ━━━━━ RATING ENGINE ━━━━━

class StatPulseRater:
    """
    Composite player rating system.
    
    Features (weighted differently by position):
    1. Goals (weighted +2.5)
    2. Assists (weighted +1.5)
    3. xG (shot quality)
    4. xA (pass quality)
    5. Progressive passes (forward ball)
    6. Duels won % (physical dominance)
    7. Touches in box (attacking threat)
    8. Errors leading to shot (defensive mistakes, -1.5)
    9. Minutes played (per-90 normalization)
    10. Match result bonus (+0.3 if won, -0.2 if lost)
    """
    
    # Position-specific weights
    WEIGHTS = {
        PlayerPosition.GK: {
            'goals': 0,
            'assists': 0,
            'xg': 0,
            'xa': 0,
            'progressive_passes': 0.05,
            'duels_won_pct': 0.30,
            'touches_in_box': 0,
            'errors_leading_to_shot': 1.5,
            'clean_sheet': 2.0,
            'saves': 0.5,
        },
        PlayerPosition.DEF: {
            'goals': 2.5,
            'assists': 1.5,
            'xg': 0.2,
            'xa': 0.2,
            'progressive_passes': 0.2,
            'duels_won_pct': 1.0,
            'touches_in_box': 0.1,
            'errors_leading_to_shot': 1.5,
            'tackles_blocks': 0.5,
        },
        PlayerPosition.MID: {
            'goals': 2.5,
            'assists': 1.5,
            'xg': 0.5,
            'xa': 0.5,
            'progressive_passes': 0.5,
            'duels_won_pct': 0.5,
            'touches_in_box': 0.3,
            'errors_leading_to_shot': 1.0,
            'pass_accuracy': 0.2,
        },
        PlayerPosition.FWD: {
            'goals': 2.5,
            'assists': 1.5,
            'xg': 1.0,
            'xa': 0.5,
            'progressive_passes': 0.2,
            'duels_won_pct': 0.2,
            'touches_in_box': 0.5,
            'errors_leading_to_shot': 0.5,
            'shot_accuracy': 0.3,
        }
    }
    
    def __init__(self):
        self.players_cache = {}
        self.tournament_stats = {}
    
    def rate_player(self, stats: PlayerStats, team_result: str = 'draw') -> PlayerRating:
        """
        Calculate player rating (0-10 scale).
        
        Methodology:
        1. Normalize per 90 minutes
        2. Apply position-specific weights
        3. Z-score normalization
        4. Apply result bonus/penalty
        5. Scale to 0-10
        """
        
        # Per-90 normalization
        if stats.minutes_played == 0:
            return None
        
        per90_multiplier = 90.0 / stats.minutes_played
        
        # Calculate base score (0-10 scale)
        weights = self.WEIGHTS[stats.position]
        
        # Component scores
        components = {
            'goals': min(stats.goals * weights.get('goals', 0) * per90_multiplier, 5.0),
            'assists': min(stats.assists * weights.get('assists', 0) * per90_multiplier, 3.0),
            'xg': min(stats.xg * weights.get('xg', 0) * per90_multiplier, 2.0),
            'xa': min(stats.xa * weights.get('xa', 0) * per90_multiplier, 1.5),
            'progressive_passes': min(stats.progressive_passes * weights.get('progressive_passes', 0) * per90_multiplier, 1.5),
            'duels_won_pct': (stats.duels_won_pct / 100.0) * weights.get('duels_won_pct', 0),
            'touches_in_box': min(stats.touches_in_box * weights.get('touches_in_box', 0) * per90_multiplier, 1.5),
            'errors': -min(stats.errors_leading_to_shot * weights.get('errors_leading_to_shot', 0), 2.0),
        }
        
        # Sum components
        base_score = sum(components.values())
        
        # Apply result bonus/penalty
        if team_result == 'win':
            result_bonus = 0.3
        elif team_result == 'loss':
            result_bonus = -0.2
        else:
            result_bonus = 0.0
        
        # Final rating (0-10)
        final_rating = min(max(base_score + result_bonus, 0.0), 10.0)
        
        return PlayerRating(
            player_id=stats.player_id,
            player_name=stats.player_name,
            team=stats.team,
            position=stats.position,
            match_rating=round(final_rating, 2),
            rating_per90=round(final_rating * per90_multiplier, 2),
            components=components,
            timestamp=datetime.now()
        )
    
    def get_tournament_leaderboard(self, limit: int = 50) -> List[TournamentRanking]:
        """Get top-rated players across tournament"""
        # TODO: Query from database and calculate averages
        return []


# ━━━━━ GLOBAL RATER INSTANCE ━━━━━
rater = StatPulseRater()


# ━━━━━ API ENDPOINTS ━━━━━

@router.post("/rate", response_model=PlayerRating, tags=["Ratings"])
async def rate_player_match(stats: PlayerStats, team_result: str = "draw"):
    """Rate a player for a specific match"""
    try:
        rating = rater.rate_player(stats, team_result)
        if rating is None:
            raise HTTPException(status_code=400, detail="Invalid player stats")
        return rating
    except Exception as e:
        logger.error(f"Rating error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/player/{player_name}", tags=["Ratings"])
async def get_player_stats(player_name: str):
    """Get player tournament statistics and ratings"""
    # TODO: Fetch from database
    return {
        "player_name": player_name,
        "matches_played": 0,
        "avg_rating": 0.0,
        "total_goals": 0,
        "total_assists": 0,
        "ratings_history": []
    }


@router.get("/leaderboard", tags=["Rankings"])
async def get_tournament_leaderboard(
    position: Optional[str] = Query(None),
    limit: int = Query(50, le=500)
):
    """Get tournament player leaderboard with optional position filter"""
    # TODO: Implement full leaderboard from database
    leaderboard = [
        {
            "rank": 1,
            "player_name": "Player Name",
            "team": "Team",
            "position": "Forward",
            "avg_rating": 8.5,
            "matches": 2,
            "goals": 2,
            "assists": 1
        }
    ]
    return {"leaderboard": leaderboard}


@router.get("/team/{team_name}", tags=["Team Stats"])
async def get_team_roster(team_name: str):
    """Get all players from a team with their ratings"""
    # TODO: Query team roster from database
    return {
        "team": team_name,
        "players": [],
        "avg_team_rating": 0.0
    }


@router.get("/best-xi", tags=["Rankings"])
async def get_best_xi():
    """Get tournament's best XI (best formation) based on ratings"""
    return {
        "formation": "4-3-3",
        "players": {
            "goalkeeper": {"name": "Player", "rating": 8.2},
            "defenders": [],
            "midfielders": [],
            "forwards": []
        }
    }


@router.get("/match/{match_id}/ratings", tags=["Match Stats"])
async def get_match_player_ratings(match_id: str):
    """Get all player ratings from a specific match"""
    # TODO: Query from database
    return {
        "match_id": match_id,
        "team_a_ratings": [],
        "team_b_ratings": [],
        "player_of_match": None
    }
