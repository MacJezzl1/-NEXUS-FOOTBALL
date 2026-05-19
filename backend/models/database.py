"""
⚽ NEXUS FOOTBALL — Database Models & Migrations
Using SQLAlchemy ORM with Alembic migrations
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, ForeignKey, Enum, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum

Base = declarative_base()

# ━━━━━ ENUMS ━━━━━

class PlayerPosition(str, PyEnum):
    GK = "goalkeeper"
    DEF = "defender"
    MID = "midfielder"
    FWD = "forward"

class MatchStatus(str, PyEnum):
    UPCOMING = "upcoming"
    LIVE = "live"
    COMPLETED = "completed"
    POSTPONED = "postponed"

# ━━━━━ MODELS ━━━━━

class Team(Base):
    """World Cup team data"""
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    iso_code = Column(String(3), unique=True)
    fifa_rank = Column(Integer)
    elo_rating = Column(Float, default=1600.0)
    group = Column(String(1))  # A, B, C, D, E, F, G, H
    confederation = Column(String(50))  # CONMEBOL, UEFA, etc.
    flag_emoji = Column(String(5))
    
    # Relationships
    matches_home = relationship("Match", foreign_keys="Match.team_a_id", back_populates="team_a")
    matches_away = relationship("Match", foreign_keys="Match.team_b_id", back_populates="team_b")
    players = relationship("Player", back_populates="team")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Player(Base):
    """World Cup player data"""
    __tablename__ = "players"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    position = Column(Enum(PlayerPosition), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    shirt_number = Column(Integer)
    height_cm = Column(Integer)
    date_of_birth = Column(DateTime)
    country_code = Column(String(3))
    club = Column(String(150))
    
    # Career stats
    international_caps = Column(Integer, default=0)
    international_goals = Column(Integer, default=0)
    
    # Tournament stats
    tournament_goals = Column(Integer, default=0)
    tournament_assists = Column(Integer, default=0)
    tournament_avg_rating = Column(Float, default=0.0)
    matches_played = Column(Integer, default=0)
    
    # Relationships
    team = relationship("Team", back_populates="players")
    match_ratings = relationship("PlayerMatchRating", back_populates="player")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Match(Base):
    """World Cup match data"""
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True)
    match_id = Column(String(50), unique=True, nullable=False)
    team_a_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    team_b_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    
    # Match details
    stage = Column(String(50))  # Group, Round of 16, QF, SF, Final
    group = Column(String(1))
    match_day = Column(Integer)
    kickoff_time = Column(DateTime, nullable=False)
    venue = Column(String(200))
    city = Column(String(100))
    
    # Match status
    status = Column(Enum(MatchStatus), default=MatchStatus.UPCOMING)
    
    # Results
    score_a = Column(Integer)
    score_b = Column(Integer)
    xg_a = Column(Float)
    xg_b = Column(Float)
    possession_a = Column(Float)  # Percentage
    possession_b = Column(Float)
    shots_a = Column(Integer)
    shots_b = Column(Integer)
    shots_on_target_a = Column(Integer)
    shots_on_target_b = Column(Integer)
    
    # Statistics
    corners_a = Column(Integer, default=0)
    corners_b = Column(Integer, default=0)
    fouls_a = Column(Integer, default=0)
    fouls_b = Column(Integer, default=0)
    cards_yellow_a = Column(Integer, default=0)
    cards_yellow_b = Column(Integer, default=0)
    cards_red_a = Column(Integer, default=0)
    cards_red_b = Column(Integer, default=0)
    
    # PitchOracle Predictions
    prediction_win_prob_a = Column(Float)  # Probability of team_a win
    prediction_draw_prob = Column(Float)
    prediction_win_prob_b = Column(Float)  # Probability of team_b win
    prediction_confidence = Column(Float)
    
    # Relationships
    team_a = relationship("Team", foreign_keys=[team_a_id], back_populates="matches_home")
    team_b = relationship("Team", foreign_keys=[team_b_id], back_populates="matches_away")
    player_ratings = relationship("PlayerMatchRating", back_populates="match", cascade="all, delete-orphan")
    events = relationship("MatchEvent", back_populates="match", cascade="all, delete-orphan")
    ai_reports = relationship("AIReport", back_populates="match", cascade="all, delete-orphan")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PlayerMatchRating(Base):
    """StatPulse — Individual player performance ratings per match"""
    __tablename__ = "player_match_ratings"
    
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    
    # Performance metrics
    rating_0_10 = Column(Float)  # Overall rating 0-10
    goals = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    xg = Column(Float, default=0.0)
    xa = Column(Float, default=0.0)
    progressive_passes = Column(Integer, default=0)
    duels_won_pct = Column(Float, default=0.0)
    touches_in_box = Column(Integer, default=0)
    errors_leading_to_shot = Column(Integer, default=0)
    minutes_played = Column(Integer, default=0)
    
    # Bonus/penalty
    team_result = Column(String(10))  # win, draw, loss
    is_player_of_match = Column(Boolean, default=False)
    
    # Detailed breakdown (JSON for flexibility)
    component_scores = Column(JSON)  # {goals: 2.5, assists: 1.5, ...}
    
    # Relationships
    player = relationship("Player", back_populates="match_ratings")
    match = relationship("Match", back_populates="player_ratings")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MatchEvent(Base):
    """Detailed match events (goals, cards, substitutions, etc.)"""
    __tablename__ = "match_events"
    
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    
    event_type = Column(String(50))  # goal, card, substitution, etc.
    minute = Column(Integer)
    minute_extended = Column(Integer)  # For extra time
    team_side = Column(String(1))  # A or B
    player_name = Column(String(150))
    description = Column(Text)
    
    # For goals
    is_penalty = Column(Boolean, default=False)
    is_own_goal = Column(Boolean, default=False)
    
    # For substitutions
    player_off_name = Column(String(150))
    
    # Relationships
    match = relationship("Match", back_populates="events")
    
    created_at = Column(DateTime, default=datetime.utcnow)


class AIReport(Base):
    """MatchMind AI — Generated match reports"""
    __tablename__ = "ai_reports"
    
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    
    report_type = Column(String(20))  # prematch, inmatch, postmatch
    content = Column(Text, nullable=False)
    summary = Column(String(500))
    
    # Models used
    models_used = Column(JSON)  # List of AI models
    confidence_score = Column(Float)
    
    # Language
    language = Column(String(5), default="en")
    
    # Export formats
    pdf_url = Column(String(500))
    html_url = Column(String(500))
    
    # Relationships
    match = relationship("Match", back_populates="ai_reports")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PredictionAccuracy(Base):
    """Track PitchOracle prediction accuracy"""
    __tablename__ = "prediction_accuracy"
    
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    
    predicted_winner = Column(String(100))
    actual_winner = Column(String(100))
    predicted_draw = Column(Boolean)
    was_correct = Column(Boolean)
    
    prediction_confidence = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class UserPrediction(Base):
    """User-submitted predictions (gamification)"""
    __tablename__ = "user_predictions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(100), nullable=False)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    
    predicted_winner = Column(String(100))
    predicted_score = Column(String(10))  # e.g., "2-1"
    
    is_correct = Column(Boolean)
    points_earned = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
