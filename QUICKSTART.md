# ⚽ NEXUS FOOTBALL — Quick Start Guide

Get up and running with the World Cup 2026 Intelligence Platform in 5 minutes.

## Prerequisites

- Docker & Docker Compose installed
- Git installed
- ~3GB disk space
- API keys (optional, for advanced features)

## One-Command Startup

```bash
git clone https://github.com/yourusername/nexus-football.git
cd nexus-football
docker-compose up
```

That's it! Open http://localhost:3000 in your browser.

---

## Manual Setup (Development)

### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/nexus-football.git
cd nexus-football
```

### Step 2: Backend Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Run migrations (if DB set up)
python backend/manage.py migrate

# Start backend server
python -m uvicorn backend.main:app --reload
```

Backend will run on **http://localhost:8000**

### Step 3: Frontend Setup (New Terminal)
```bash
cd frontend
npm install
npm start
```

Frontend will run on **http://localhost:3000**

### Step 4: Database & Cache (New Terminal)
```bash
docker-compose up postgres redis
```

---

## Accessing the Platform

### Frontend Dashboard
- **URL**: http://localhost:3000
- **Main systems**: PitchOracle, StatPulse, MatchMind AI

### Backend API
- **URL**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs
- **Endpoints**:
  - `/api/v1/pitchoracle/predict` — Get match predictions
  - `/api/v1/statpulse/leaderboard` — Get player rankings
  - `/api/v1/matchmind/generate-report` — Generate AI reports

---

## Environment Setup

Create `.env` file from template:

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
# Database
DATABASE_URL=postgresql://nexus:nexus_password@localhost:5432/nexus_football

# AI Services
ANTHROPIC_API_KEY=sk-xxx
OPENAI_API_KEY=sk-xxx
TOGETHER_API_KEY=xxx

# API Keys
RAPIDAPI_KEY=xxx
```

---

## Common Commands

### Backend
```bash
# Run tests
pytest backend/tests -v

# Format code
black backend/

# Lint
ruff check backend/

# Start with reload
python -m uvicorn backend.main:app --reload --host 0.0.0.0

# Start Celery worker
celery -A backend.queue.tasks worker --loglevel=info
```

### Frontend
```bash
# Run tests
npm test

# Format code
npm run format

# Lint
npm run lint

# Build for production
npm run build

# Start development server
npm start
```

### Docker
```bash
# Start all services
docker-compose up

# Start specific service
docker-compose up frontend

# View logs
docker-compose logs -f backend

# Stop all services
docker-compose down

# Remove volumes (reset data)
docker-compose down -v
```

---

## API Examples

### Get Match Predictions (PitchOracle)

```bash
curl -X POST http://localhost:8000/api/v1/pitchoracle/predict \
  -H "Content-Type: application/json" \
  -d '{
    "team_a": "Argentina",
    "team_b": "Brazil",
    "team_a_stats": {
      "team_name": "Argentina",
      "fifa_rank": 1,
      "elo_rating": 2100,
      "recent_form": ["W", "W", "D", "W", "W"],
      "goals_scored_avg": 2.1,
      "goals_conceded_avg": 0.8,
      "xg_avg": 1.9
    },
    "team_b_stats": {
      "team_name": "Brazil",
      "fifa_rank": 2,
      "elo_rating": 2080,
      "recent_form": ["W", "W", "W", "D", "W"],
      "goals_scored_avg": 2.3,
      "goals_conceded_avg": 0.9,
      "xg_avg": 2.1
    }
  }'
```

### Get Player Ratings (StatPulse)

```bash
curl http://localhost:8000/api/v1/statpulse/leaderboard?limit=10
```

### Generate AI Report (MatchMind)

```bash
curl -X POST http://localhost:8000/api/v1/matchmind/generate-report \
  -H "Content-Type: application/json" \
  -d '{
    "match_id": "wc2026_group_a_1",
    "team_a": "USA",
    "team_b": "England",
    "report_type": "prematch"
  }'
```

---

## Project Structure Quick Reference

```
nexus-football/
├── backend/              # FastAPI backend
│   ├── main.py          # Main app
│   ├── apis/            # REST endpoints
│   │   ├── pitchoracle.py
│   │   ├── statpulse.py
│   │   └── matchmind.py
│   ├── services/        # Business logic
│   └── requirements.txt
│
├── frontend/            # React frontend
│   ├── src/
│   │   ├── App.jsx
│   │   ├── pages/       # Page components
│   │   └── components/  # React components
│   └── package.json
│
├── data/               # Data pipeline
│   └── collectors/     # Data collection scripts
│
├── docker-compose.yml  # Container orchestration
├── README.md          # Documentation
└── CONTRIBUTING.md    # Contributing guide
```

---

## Troubleshooting

### Port Already in Use

```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

### Database Connection Error

```bash
# Check if PostgreSQL is running
docker-compose ps

# View database logs
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up postgres
```

### React Module Not Found

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

---

## Next Steps

1. **Explore the API** → http://localhost:8000/api/docs
2. **Check the Dashboard** → http://localhost:3000
3. **Read Contributing Guide** → See CONTRIBUTING.md
4. **Set up API Keys** → See .env.example
5. **Run Tests** → `pytest backend/tests`

---

## Need Help?

- 📖 Read the full README.md
- 🤝 Check CONTRIBUTING.md for guidelines
- 🐛 Open an issue on GitHub
- 💬 Join our discussions

---

**Ready to analyze the World Cup 2026?** ⚽

⚽ **NEXUS FOOTBALL** — Know the Game. Master the Data.
