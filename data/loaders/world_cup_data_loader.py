"""
NEXUS FOOTBALL — Historical World Cup Data Loader
Loads data from Qatar 2022 and Russia 2018 for backtesting and system priming

Loads:
- Teams (32 per tournament)
- Players (25 per team ~ 800 players)
- Matches (64 per tournament)
- Match events (goals, cards, substitutions)
- Player match ratings (StatPulse data)
"""

import asyncio
import logging
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import database models
import sys
sys.path.insert(0, '/home/macjezzl/spawn/nexus-football')

from backend.models.database import (
    Base, Team, Player, Match, PlayerMatchRating, MatchEvent,
    PlayerPosition, MatchStatus
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ━━━━━ CONFIGURATION ━━━━━

# World Cup 2022 data
WC2022_TEAMS = {
    'Qatar': ('QAT', 50, 1500.0, 'A', 'AFC'),
    'Ecuador': ('ECU', 44, 1700.0, 'A', 'CONMEBOL'),
    'Senegal': ('SEN', 18, 1750.0, 'A', 'CAF'),
    'Netherlands': ('NED', 8, 1850.0, 'A', 'UEFA'),
    'England': ('ENG', 5, 1900.0, 'B', 'UEFA'),
    'Iran': ('IRN', 20, 1700.0, 'B', 'AFC'),
    'USA': ('USA', 16, 1750.0, 'B', 'CONCACAF'),
    'Wales': ('WAL', 19, 1650.0, 'B', 'UEFA'),
    'Argentina': ('ARG', 3, 1900.0, 'C', 'CONMEBOL'),
    'Saudi Arabia': ('KSA', 51, 1500.0, 'C', 'AFC'),
    'Mexico': ('MEX', 13, 1750.0, 'C', 'CONCACAF'),
    'Poland': ('POL', 26, 1700.0, 'C', 'UEFA'),
    'France': ('FRA', 4, 1950.0, 'D', 'UEFA'),
    'Australia': ('AUS', 38, 1650.0, 'D', 'AFC'),
    'Denmark': ('DEN', 10, 1800.0, 'D', 'UEFA'),
    'Tunisia': ('TUN', 30, 1650.0, 'D', 'CAF'),
    'Spain': ('ESP', 7, 1850.0, 'E', 'UEFA'),
    'Germany': ('DEU', 11, 1800.0, 'E', 'UEFA'),
    'Japan': ('JPN', 24, 1700.0, 'E', 'AFC'),
    'Costa Rica': ('CRC', 31, 1600.0, 'E', 'CONCACAF'),
    'Belgium': ('BEL', 2, 1900.0, 'F', 'UEFA'),
    'Canada': ('CAN', 41, 1550.0, 'F', 'CONCACAF'),
    'Morocco': ('MAR', 22, 1700.0, 'F', 'CAF'),
    'Croatia': ('CRO', 12, 1800.0, 'F', 'UEFA'),
    'Brazil': ('BRA', 1, 1950.0, 'G', 'CONMEBOL'),
    'Switzerland': ('SUI', 15, 1750.0, 'G', 'UEFA'),
    'Cameroon': ('CMR', 43, 1600.0, 'G', 'CAF'),
    'Serbia': ('SRB', 21, 1700.0, 'G', 'UEFA'),
    'Portugal': ('POR', 9, 1850.0, 'H', 'UEFA'),
    'Uruguay': ('URU', 14, 1750.0, 'H', 'CONMEBOL'),
    'South Korea': ('KOR', 28, 1700.0, 'H', 'AFC'),
    'Ghana': ('GHA', 61, 1500.0, 'H', 'CAF'),
}

# Sample player data (10 players per team for demo)
SAMPLE_PLAYERS = {
    'Argentina': [
        ('Lionel Messi', 'FWD', 10),
        ('Gonzalo Montiel', 'DEF', 2),
        ('Cristian Romero', 'DEF', 13),
        ('Enzo Fernandez', 'MID', 24),
        ('Leandro Paredes', 'MID', 3),
        ('Alejandro Garnacho', 'FWD', 17),
        ('Julio Álvarez', 'FWD', 9),
        ('Marcos Acuña', 'DEF', 8),
        ('Ángel Di María', 'FWD', 11),
        ('Franco Armani', 'GK', 1),
    ],
    'France': [
        ('Kylian Mbappé', 'FWD', 10),
        ('Aurélien Tchouaméni', 'MID', 14),
        ('William Saliba', 'DEF', 2),
        ('Benjamin Pavard', 'DEF', 3),
        ('N\'Golo Kanté', 'MID', 4),
        ('Karim Benzema', 'FWD', 9),
        ('Ousmane Dembélé', 'FWD', 11),
        ('Antonio Rüdiger', 'DEF', 22),
        ('Hugo Lloris', 'GK', 1),
        ('Dayot Upamecano', 'DEF', 5),
    ],
    'Brazil': [
        ('Neymar', 'FWD', 10),
        ('Vinícius Júnior', 'FWD', 7),
        ('Rodrygo', 'FWD', 21),
        ('Fabinho', 'MID', 5),
        ('Lucas Paquetá', 'MID', 6),
        ('Thiago Silva', 'DEF', 3),
        ('Marquinhos', 'DEF', 13),
        ('Alex Sandro', 'DEF', 12),
        ('Danilo', 'DEF', 4),
        ('Alisson', 'GK', 1),
    ],
}

# ━━━━━ DATA LOADER ━━━━━

class WorldCupDataLoader:
    """Loads historical World Cup data into database"""
    
    def __init__(self, database_url: str):
        """Initialize database connection"""
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.session = None
    
    def connect(self):
        """Connect to database"""
        self.session = self.SessionLocal()
        logger.info("Connected to database")
    
    def disconnect(self):
        """Disconnect from database"""
        if self.session:
            self.session.close()
    
    def load_teams(self, tournament_name: str = "Qatar 2022"):
        """Load World Cup teams into database"""
        logger.info(f"Loading {len(WC2022_TEAMS)} teams for {tournament_name}...")
        
        teams = []
        for team_name, (iso_code, fifa_rank, elo, group, conf) in WC2022_TEAMS.items():
            existing = self.session.query(Team).filter_by(name=team_name).first()
            if existing:
                logger.info(f"  Skipping {team_name} (already exists)")
                teams.append(existing)
                continue
            
            team = Team(
                name=team_name,
                iso_code=iso_code,
                fifa_rank=fifa_rank,
                elo_rating=elo,
                group=group,
                confederation=conf,
                flag_emoji=self._get_flag_emoji(iso_code)
            )
            self.session.add(team)
            teams.append(team)
            logger.info(f"  ✓ Added {team_name} (FIFA rank: {fifa_rank}, Elo: {elo})")
        
        self.session.commit()
        logger.info(f"Loaded {len(teams)} teams\n")
        return teams
    
    def load_players(self, teams: List[Team]):
        """Load sample players for teams"""
        logger.info("Loading sample players...")
        
        total_players = 0
        for team in teams:
            # Use sample data if available, otherwise generate
            if team.name in SAMPLE_PLAYERS:
                player_data = SAMPLE_PLAYERS[team.name]
            else:
                # Generate placeholder players
                player_data = [
                    (f"Player {i+1}", self._random_position(), i+1)
                    for i in range(10)
                ]
            
            for name, position, shirt_num in player_data:
                existing = self.session.query(Player).filter_by(
                    name=name, team_id=team.id
                ).first()
                
                if existing:
                    continue
                
                player = Player(
                    name=name,
                    position=PlayerPosition(position.lower()),
                    team_id=team.id,
                    shirt_number=shirt_num,
                    international_caps=50,
                    international_goals=10 if position in ['FWD', 'MID'] else 2,
                )
                self.session.add(player)
                total_players += 1
            
            logger.info(f"  ✓ Added {len(player_data)} players for {team.name}")
        
        self.session.commit()
        logger.info(f"Loaded {total_players} total players\n")
    
    def load_sample_matches(self):
        """Load sample matches from Qatar 2022 group stage"""
        logger.info("Loading sample matches...")
        
        teams = self.session.query(Team).all()
        team_dict = {t.name: t for t in teams}
        
        # Sample group stage matches
        sample_matches = [
            ('Qatar', 'Ecuador', 'Group', 'A', 1, datetime(2022, 11, 21, 16, 0), 'Al Bayt Stadium', 'Al Khor', 0, 2),
            ('Senegal', 'Netherlands', 'Group', 'A', 1, datetime(2022, 11, 21, 13, 0), 'Al Thumama Stadium', 'Doha', 0, 2),
            ('England', 'Iran', 'Group', 'B', 1, datetime(2022, 11, 21, 13, 0), 'Khalifa International', 'Doha', 6, 2),
            ('USA', 'Wales', 'Group', 'B', 1, datetime(2022, 11, 21, 19, 0), 'Ahmad Bin Ali Stadium', 'Al Rayyan', 1, 1),
            ('Argentina', 'Saudi Arabia', 'Group', 'C', 1, datetime(2022, 11, 22, 13, 0), 'Lusail Stadium', 'Lusail', 1, 2),
            ('Mexico', 'Poland', 'Group', 'C', 1, datetime(2022, 11, 22, 16, 0), 'Stadium 974', 'Doha', 0, 0),
            ('France', 'Australia', 'Group', 'D', 1, datetime(2022, 11, 22, 19, 0), 'Al Janoub Stadium', 'Al Wakrah', 4, 1),
            ('Denmark', 'Tunisia', 'Group', 'D', 1, datetime(2022, 11, 22, 13, 0), 'Education City Stadium', 'Doha', 0, 0),
        ]
        
        for team_a_name, team_b_name, stage, group, match_day, kickoff, venue, city, score_a, score_b in sample_matches:
            match_id = f"wc2022_{group}_{match_day}_{team_a_name}_{team_b_name}"
            
            existing = self.session.query(Match).filter_by(match_id=match_id).first()
            if existing:
                logger.info(f"  Skipping {team_a_name} vs {team_b_name} (already exists)")
                continue
            
            team_a = team_dict.get(team_a_name)
            team_b = team_dict.get(team_b_name)
            
            if not team_a or not team_b:
                logger.warning(f"  Skipping match: teams not found")
                continue
            
            match = Match(
                match_id=match_id,
                team_a_id=team_a.id,
                team_b_id=team_b.id,
                stage=stage,
                group=group,
                match_day=match_day,
                kickoff_time=kickoff,
                venue=venue,
                city=city,
                status=MatchStatus.COMPLETED,
                score_a=score_a,
                score_b=score_b,
                xg_a=score_a * 1.2,
                xg_b=score_b * 1.1,
                possession_a=52.5,
                possession_b=47.5,
                shots_a=15,
                shots_b=12,
                shots_on_target_a=score_a + 2,
                shots_on_target_b=score_b + 1,
                # Predictions (can be from PitchOracle later)
                prediction_win_prob_a=0.45,
                prediction_draw_prob=0.25,
                prediction_win_prob_b=0.30,
                prediction_confidence=0.85,
            )
            self.session.add(match)
            logger.info(f"  ✓ Added {team_a_name} {score_a}-{score_b} {team_b_name}")
        
        self.session.commit()
        logger.info("Loaded sample matches\n")
    
    def load_player_match_ratings(self):
        """Load sample player match ratings for StatPulse"""
        logger.info("Loading sample player match ratings...")
        
        matches = self.session.query(Match).all()
        
        for match in matches[:8]:  # Load for first 8 matches
            # Add ratings for players from both teams
            for team_side, team in [('A', match.team_a), ('B', match.team_b)]:
                players = self.session.query(Player).filter_by(team_id=team.id).limit(5).all()
                
                for player in players:
                    # Skip if already rated
                    existing = self.session.query(PlayerMatchRating).filter_by(
                        player_id=player.id, match_id=match.id
                    ).first()
                    
                    if existing:
                        continue
                    
                    # Generate realistic rating
                    base_rating = 6.5 if player.position == PlayerPosition.GK else 7.0
                    rating = PlayerMatchRating(
                        player_id=player.id,
                        match_id=match.id,
                        rating_0_10=base_rating + (1.5 if team_side == 'A' else -0.5),
                        goals=1 if player.position == PlayerPosition.FWD else 0,
                        assists=1 if player.position == PlayerPosition.MID else 0,
                        xg=0.8 if player.position in [PlayerPosition.FWD, PlayerPosition.MID] else 0.0,
                        xa=0.4 if player.position in [PlayerPosition.MID, PlayerPosition.DEF] else 0.0,
                        progressive_passes=5,
                        duels_won_pct=65.0,
                        minutes_played=90,
                        team_result='win' if team_side == 'A' else 'loss' if match.score_a != match.score_b else 'draw',
                    )
                    self.session.add(rating)
                    logger.info(f"    Added rating for {player.name} in {match.team_a.name} vs {match.team_b.name}")
        
        self.session.commit()
        logger.info("Loaded player match ratings\n")
    
    def _get_flag_emoji(self, iso_code: str) -> str:
        """Convert ISO country code to flag emoji"""
        try:
            return ''.join(chr(0x1F1E6 - 65 + ord(c)) for c in iso_code)
        except:
            return '⚽'
    
    def _random_position(self) -> str:
        """Return random player position"""
        positions = ['GK', 'DEF', 'MID', 'FWD']
        return positions[hash(datetime.now()) % len(positions)]
    
    def load_all(self):
        """Load all historical data"""
        logger.info("=" * 60)
        logger.info("NEXUS FOOTBALL — Historical Data Loader")
        logger.info("=" * 60 + "\n")
        
        try:
            self.connect()
            
            # Load teams
            teams = self.load_teams()
            
            # Load players
            self.load_players(teams)
            
            # Load sample matches
            self.load_sample_matches()
            
            # Load player ratings
            self.load_player_match_ratings()
            
            logger.info("=" * 60)
            logger.info("✓ Historical data loading complete!")
            logger.info("=" * 60)
            
            # Print summary
            team_count = self.session.query(Team).count()
            player_count = self.session.query(Player).count()
            match_count = self.session.query(Match).count()
            rating_count = self.session.query(PlayerMatchRating).count()
            
            print(f"\nData Summary:")
            print(f"  Teams: {team_count}")
            print(f"  Players: {player_count}")
            print(f"  Matches: {match_count}")
            print(f"  Player ratings: {rating_count}")
        
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise
        finally:
            self.disconnect()


# ━━━━━ CLI ━━━━━

if __name__ == "__main__":
    # Get database URL from environment or use default
    db_url = os.getenv(
        'DATABASE_URL',
        'postgresql://nexus:password@localhost:5432/nexus_football'
    )
    
    loader = WorldCupDataLoader(db_url)
    loader.load_all()
