"""
⚽ NEXUS FOOTBALL — Backend Tests
Comprehensive test suite for PitchOracle, StatPulse, and MatchMind AI
"""

import pytest
from datetime import datetime
from backend.apis.pitchoracle import EnsemblePredictorV1, TeamStats, MatchPredictionRequest
from backend.apis.statpulse import StatPulseRater, PlayerStats, PlayerPosition

# ━━━━━ FIXTURES ━━━━━

@pytest.fixture
def mock_team_stats_a():
    """Mock team stats for team A"""
    return TeamStats(
        team_name="Argentina",
        fifa_rank=1,
        elo_rating=2100,
        recent_form=['W', 'W', 'D', 'W', 'W'],
        goals_scored_avg=2.1,
        goals_conceded_avg=0.8,
        xg_avg=1.9
    )

@pytest.fixture
def mock_team_stats_b():
    """Mock team stats for team B"""
    return TeamStats(
        team_name="Brazil",
        fifa_rank=2,
        elo_rating=2080,
        recent_form=['W', 'W', 'W', 'D', 'W'],
        goals_scored_avg=2.3,
        goals_conceded_avg=0.9,
        xg_avg=2.1
    )

@pytest.fixture
def predictor():
    """Initialize predictor"""
    return EnsemblePredictorV1()

@pytest.fixture
def rater():
    """Initialize rater"""
    return StatPulseRater()

# ━━━━━ PITCHORACLE TESTS ━━━━━

class TestPitchOracle:
    """Test PitchOracle prediction engine"""
    
    def test_predictor_initialization(self, predictor):
        """Test predictor loads models"""
        assert predictor.models is not None
        assert len(predictor.models) == 5  # 5 models in ensemble
    
    def test_feature_extraction(self, predictor, mock_team_stats_a, mock_team_stats_b):
        """Test feature extraction"""
        features = predictor._extract_features(mock_team_stats_a, mock_team_stats_b)
        
        assert features is not None
        assert len(features) == 7  # 7 features
        assert isinstance(features, __import__('numpy').ndarray)
    
    def test_form_score_calculation(self, predictor):
        """Test form score calculation"""
        recent_form = ['W', 'W', 'D', 'L', 'W']
        score = predictor._calculate_form_score(recent_form)
        
        # W=3, W=3, D=1, L=0, W=3 = 10
        assert score == 10
    
    def test_prediction_output(self, predictor, mock_team_stats_a, mock_team_stats_b):
        """Test prediction output format"""
        prediction = predictor.predict(mock_team_stats_a, mock_team_stats_b)
        
        assert 'win_prob' in prediction
        assert 'draw_prob' in prediction
        assert 'loss_prob' in prediction
        assert 'confidence' in prediction
        
        # Probabilities must sum to 1.0
        total = prediction['win_prob'] + prediction['draw_prob'] + prediction['loss_prob']
        assert abs(total - 1.0) < 0.01
    
    def test_prediction_confidence_range(self, predictor, mock_team_stats_a, mock_team_stats_b):
        """Test confidence is in valid range"""
        prediction = predictor.predict(mock_team_stats_a, mock_team_stats_b)
        
        assert 0.0 <= prediction['confidence'] <= 1.0
    
    def test_equal_strength_teams(self, predictor):
        """Test prediction for equally matched teams"""
        team_a = TeamStats(
            team_name="Team A",
            fifa_rank=10,
            elo_rating=2000,
            recent_form=['W', 'D', 'W', 'D', 'W'],
            goals_scored_avg=1.5,
            goals_conceded_avg=1.5,
            xg_avg=1.5
        )
        team_b = TeamStats(
            team_name="Team B",
            fifa_rank=10,
            elo_rating=2000,
            recent_form=['W', 'D', 'W', 'D', 'W'],
            goals_scored_avg=1.5,
            goals_conceded_avg=1.5,
            xg_avg=1.5
        )
        
        prediction = predictor.predict(team_a, team_b)
        
        # For equal teams, draw probability should be highest or close to others
        assert prediction['draw_prob'] >= 0.2

# ━━━━━ STATPULSE TESTS ━━━━━

class TestStatPulse:
    """Test StatPulse player rating engine"""
    
    def test_rater_initialization(self, rater):
        """Test rater initializes with weight configs"""
        assert PlayerPosition.GK in rater.WEIGHTS
        assert PlayerPosition.DEF in rater.WEIGHTS
        assert PlayerPosition.MID in rater.WEIGHTS
        assert PlayerPosition.FWD in rater.WEIGHTS
    
    def test_player_rating_range(self, rater):
        """Test player ratings are in 0-10 range"""
        stats = PlayerStats(
            player_id="p1",
            player_name="Test Player",
            team="Argentina",
            position=PlayerPosition.FWD,
            minutes_played=90,
            goals=2,
            assists=1,
            xg=1.5,
            xa=0.8
        )
        
        rating = rater.rate_player(stats, team_result='win')
        
        assert rating is not None
        assert 0.0 <= rating.match_rating <= 10.0
    
    def test_position_specific_weights(self, rater):
        """Test that different positions are weighted differently"""
        # Create identical stats but different positions
        stats_fwd = PlayerStats(
            player_id="p1",
            player_name="Test Player",
            team="Team",
            position=PlayerPosition.FWD,
            minutes_played=90,
            goals=2,
            assists=0,
            xg=1.5,
            xa=0.0
        )
        
        stats_def = PlayerStats(
            player_id="p2",
            player_name="Test Player",
            team="Team",
            position=PlayerPosition.DEF,
            minutes_played=90,
            goals=2,
            assists=0,
            xg=1.5,
            xa=0.0
        )
        
        rating_fwd = rater.rate_player(stats_fwd)
        rating_def = rater.rate_player(stats_def)
        
        # Forward's goals should be weighted more heavily
        assert rating_fwd.match_rating != rating_def.match_rating
    
    def test_player_of_match_bonus(self, rater):
        """Test player of match bonus"""
        stats = PlayerStats(
            player_id="p1",
            player_name="Test Player",
            team="Team",
            position=PlayerPosition.FWD,
            minutes_played=90,
            goals=1,
            assists=1
        )
        
        rating_win = rater.rate_player(stats, team_result='win')
        rating_loss = rater.rate_player(stats, team_result='loss')
        
        # Win should give higher rating
        assert rating_win.match_rating > rating_loss.match_rating
    
    def test_zero_minutes_handling(self, rater):
        """Test handling of players with 0 minutes"""
        stats = PlayerStats(
            player_id="p1",
            player_name="Test Player",
            team="Team",
            position=PlayerPosition.FWD,
            minutes_played=0,
            goals=0
        )
        
        rating = rater.rate_player(stats)
        
        # Should return None or handle gracefully
        assert rating is None

# ━━━━━ INTEGRATION TESTS ━━━━━

class TestIntegration:
    """Integration tests for the ecosystem"""
    
    def test_prediction_to_report_pipeline(self, predictor, rater):
        """Test flow from prediction to AI report"""
        # Generate prediction
        team_a = TeamStats(
            team_name="Argentina",
            fifa_rank=1,
            elo_rating=2100,
            recent_form=['W', 'W', 'D', 'W', 'W'],
            goals_scored_avg=2.1,
            goals_conceded_avg=0.8,
            xg_avg=1.9
        )
        team_b = TeamStats(
            team_name="Brazil",
            fifa_rank=2,
            elo_rating=2080,
            recent_form=['W', 'W', 'W', 'D', 'W'],
            goals_scored_avg=2.3,
            goals_conceded_avg=0.9,
            xg_avg=2.1
        )
        
        prediction = predictor.predict(team_a, team_b)
        assert prediction is not None
        
        # Rate some players
        player_stats = PlayerStats(
            player_id="p1",
            player_name="Messi",
            team="Argentina",
            position=PlayerPosition.FWD,
            minutes_played=90,
            goals=1,
            assists=1
        )
        
        rating = rater.rate_player(player_stats)
        assert rating is not None
    
    def test_multiple_predictions_consistency(self, predictor):
        """Test that predictor is consistent"""
        team_a = TeamStats(
            team_name="Argentina",
            fifa_rank=1,
            elo_rating=2100,
            recent_form=['W', 'W', 'D', 'W', 'W'],
            goals_scored_avg=2.1,
            goals_conceded_avg=0.8,
            xg_avg=1.9
        )
        team_b = TeamStats(
            team_name="Brazil",
            fifa_rank=2,
            elo_rating=2080,
            recent_form=['W', 'W', 'W', 'D', 'W'],
            goals_scored_avg=2.3,
            goals_conceded_avg=0.9,
            xg_avg=2.1
        )
        
        pred1 = predictor.predict(team_a, team_b)
        pred2 = predictor.predict(team_a, team_b)
        
        # Should return same prediction for same input
        assert pred1['win_prob'] == pred2['win_prob']

# ━━━━━ PERFORMANCE TESTS ━━━━━

class TestPerformance:
    """Performance and load tests"""
    
    def test_prediction_speed(self, predictor, mock_team_stats_a, mock_team_stats_b):
        """Test prediction generation speed"""
        import time
        
        start = time.time()
        for _ in range(100):
            predictor.predict(mock_team_stats_a, mock_team_stats_b)
        elapsed = time.time() - start
        
        # Should generate 100 predictions in < 1 second
        assert elapsed < 1.0
    
    def test_rating_speed(self, rater):
        """Test player rating speed"""
        import time
        
        start = time.time()
        for i in range(50):
            stats = PlayerStats(
                player_id=f"p{i}",
                player_name=f"Player {i}",
                team="Team",
                position=PlayerPosition.FWD,
                minutes_played=90,
                goals=1
            )
            rater.rate_player(stats)
        elapsed = time.time() - start
        
        # Should rate 50 players in < 0.5 seconds
        assert elapsed < 0.5

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=backend"])
