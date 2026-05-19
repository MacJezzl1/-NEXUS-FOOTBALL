# TEST DATA LOADING GUIDE

This guide explains how to load historical World Cup data for backtesting and system testing.

---

## Overview

The system provides two data loading options:

1. **Quick Start** (5 min) - Load sample data from Qatar 2022 group stage
2. **Full Historical** (20 min) - Load complete Qatar 2022 + Russia 2018 data

For testing, use **Quick Start**. For serious backtesting, use **Full Historical**.

---

## Quick Start — Sample Data Loading

### Prerequisites
- PostgreSQL running (local or docker-compose)
- Python 3.11+
- pip dependencies installed

### Step 1: Verify Database Connection

```bash
# Check if PostgreSQL is running
cd /home/macjezzl/spawn/nexus-football

# If using docker-compose
docker-compose up -d postgres redis

# Verify connection
psql postgresql://nexus:password@localhost:5432/nexus_football -c "SELECT version();"
```

### Step 2: Set Environment Variables

```bash
# Option A: Add to .env
cat >> .env << 'EOF'
DATABASE_URL=postgresql://nexus:password@localhost:5432/nexus_football
EOF

# Option B: Export directly
export DATABASE_URL=postgresql://nexus:password@localhost:5432/nexus_football
```

### Step 3: Run Data Loader

```bash
cd /home/macjezzl/spawn/nexus-football

# Run data loader
python -m data.loaders.world_cup_data_loader
```

**Expected output:**
```
============================================================
NEXUS FOOTBALL — Historical Data Loader
============================================================

Loading 32 teams for Qatar 2022...
  ✓ Added Argentina (FIFA rank: 3, Elo: 1900.0)
  ✓ Added France (FIFA rank: 4, Elo: 1950.0)
  ...
Loaded 32 teams

Loading sample players...
  ✓ Added 10 players for Argentina
  ✓ Added 10 players for France
  ...
Loaded 320 total players

Loading sample matches...
  ✓ Added Argentina 1-2 Saudi Arabia
  ✓ Added England 6-2 Iran
  ...
Loaded sample matches

Loading sample player match ratings...
    Added rating for Lionel Messi in Argentina vs Saudi Arabia
    ...
Loaded player match ratings

============================================================
✓ Historical data loading complete!
============================================================

Data Summary:
  Teams: 32
  Players: 320
  Matches: 8
  Player ratings: 40
```

### Step 4: Verify Data Loaded

```bash
# Query loaded data
psql postgresql://nexus:password@localhost:5432/nexus_football << 'EOF'

-- Check teams
SELECT COUNT(*) as team_count FROM teams;

-- Check players
SELECT COUNT(*) as player_count FROM players;

-- Check matches
SELECT team_a_id, team_b_id, score_a, score_b FROM matches LIMIT 5;

-- Check player ratings
SELECT COUNT(*) as rating_count FROM player_match_ratings;

EOF
```

---

## Docker Quick Start

Use docker-compose to run everything automatically:

```bash
cd /home/macjezzl/spawn/nexus-football

# Start all services
docker-compose up -d

# Run data loader (automatically runs on container startup)
docker-compose exec backend python -m data.loaders.world_cup_data_loader

# Monitor logs
docker-compose logs -f backend
```

---

## Full Historical Data Loading

For complete World Cup 2022 and 2018 data:

### Step 1: Extend Data Loader

```bash
# Edit world_cup_data_loader.py to add more matches
# Modify load_sample_matches() to include all 64 matches
# Modify WC2022_TEAMS to match actual 2022 roster

# Add 2018 World Cup data (similar structure)
```

### Step 2: Run Extended Loader

```python
# Create extended_world_cup_loader.py
# Copy world_cup_data_loader.py and expand with:
# - All 64 matches per tournament
# - Full player rosters (20-25 per team)
# - Match events (goals, cards, substitutions)
# - Realistic player ratings based on official sources

loader = WorldCupDataLoader(DATABASE_URL)
loader.load_all()
```

---

## Data Structure

### Sample Data Included

#### Teams (32)
- FIFA rankings
- Elo ratings
- Group assignments (A-H)
- Confederations

#### Players (10 per team = 320)
- Names and positions (GK, DEF, MID, FWD)
- International caps/goals
- Club information (when available)

#### Matches (8 sample from group stage)
- Scores and xG data
- Possession, shots, shot accuracy
- Match status and venue info
- Prediction probabilities (for backtesting)

#### Player Ratings (5 players × 8 matches = 40 ratings)
- Performance ratings (0-10)
- Goals, assists, xG, xA
- Possession data, duel win rates
- Team result (win/draw/loss)

---

## Using Loaded Data

### Test PitchOracle Predictions

```bash
# Start backend API
python backend/main.py

# Query predictions
curl http://localhost:8000/api/v1/predictions/match/1
```

### Test StatPulse Ratings

```bash
# Query player ratings for a match
curl http://localhost:8000/api/v1/players/ratings/match/1
```

### Test Gamification

```bash
# Make a prediction
curl -X POST http://localhost:8000/api/v1/predictions/create \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "match_id": 1, "winner": "Argentina"}'
```

---

## Data Quality Checks

The loader automatically validates:
- ✓ No duplicate teams
- ✓ Unique match IDs
- ✓ Valid player positions
- ✓ Rating scores 0-10
- ✓ Valid FIFA rankings (1-200)
- ✓ Elo ratings between 1200-2000

---

## Troubleshooting

### Error: "Connection to database failed"
```
Check:
1. PostgreSQL is running: docker ps | grep postgres
2. DATABASE_URL is correct
3. Credentials match your setup
4. Database exists: createdb nexus_football
```

### Error: "Table does not exist"
```
Solution: Run database migrations first
cd backend
alembic upgrade head
```

### Error: "Player position invalid"
```
Valid positions: goalkeeper, defender, midfielder, forward
Check spelling in SAMPLE_PLAYERS
```

### Slow loading (>5 min for sample data)
```
Solution: Optimize batch inserts
Reduce test dataset size
Check PostgreSQL resource usage: docker stats
```

---

## Next Steps

1. ✅ Load sample data (8 matches)
2. 📊 Test PitchOracle predictions on historical data
3. 📈 Calculate prediction accuracy vs actual results
4. 🎮 Test gamification with loaded matches
5. 🔍 Validate StatPulse ratings against official sources

---

## Data Sources Reference

- **FBref/soccerdata:** Historical stats, player performance
- **StatsBomb:** Event-level data, xG/xA
- **API-Football:** Live match data, detailed statistics
- **football-data.org:** Fixtures, standings, H2H records

Run `python -m data.collectors.data_pipeline` to fetch live data updates.

