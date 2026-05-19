# ⚽ NEXUS FOOTBALL — Quick Commands Reference

## 🚀 Getting Started (3 Steps)

```bash
# 1. Navigate to project
cd /home/macjezzl/spawn/nexus-football

# 2. Push to GitHub (see GITHUB_PUSH.md for auth)
git push -u origin main

# 3. Run locally
docker-compose up
# Visit: http://localhost:3000
```

## 📦 Local Development

```bash
# Start everything
docker-compose up

# Start specific service
docker-compose up backend
docker-compose up frontend
docker-compose up postgres

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop everything
docker-compose down

# Reset database
docker-compose down -v
docker-compose up postgres
```

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-asyncio

# Run all tests
pytest backend/tests -v --cov

# Run specific test
pytest backend/tests/test_apis.py::TestPitchOracle -v

# Run with coverage report
pytest backend/tests -v --cov=backend --cov-report=html
```

## 📝 Code Quality

```bash
# Format code
black backend/
black frontend/src

# Lint Python
ruff check backend/
flake8 backend/

# Lint JavaScript
cd frontend && npm run lint
npm run format
```

## 🔄 Git Workflow

```bash
# Check status
git status

# View commits
git log --oneline -10

# Create feature branch
git checkout -b feature/new-feature

# Add changes
git add .

# Commit
git commit -m "feat: description"

# Push
git push -u origin feature/new-feature

# Create pull request
# Go to: https://github.com/MacJezzl1/-NEXUS-FOOTBALL/pulls
```

## 🚢 Deployment

### Vercel (Frontend) - 5 minutes
```bash
# Connect GitHub repo to Vercel at https://vercel.com
# Set environment variable:
REACT_APP_API_URL=https://your-backend-url.com
# Auto-deploys on git push
```

### Railway (Backend) - 10 minutes
```bash
# 1. Go to https://railway.app
# 2. Connect GitHub repo
# 3. Add environment variables:
DATABASE_URL=...
REDIS_URL=...
ANTHROPIC_API_KEY=...

# 4. Deploy
railway up
```

### AWS (Production) - 30 minutes
```bash
# Deploy with CloudFormation
aws cloudformation create-stack \
  --stack-name nexus-football-prod \
  --template-body file://infrastructure/aws-cloudformation.json
```

### Local (Docker)
```bash
# Build images
docker build -t nexus-backend ./backend
docker build -t nexus-frontend ./frontend

# Run backend
docker run -p 8000:8000 nexus-backend

# Run frontend
docker run -p 3000:3000 nexus-frontend
```

## 📊 API Testing

```bash
# Health check
curl http://localhost:8000/health

# Get predictions
curl -X POST http://localhost:8000/api/v1/pitchoracle/predict \
  -H "Content-Type: application/json" \
  -d '{"team_a":"Argentina","team_b":"Brazil",...}'

# Get leaderboard
curl http://localhost:8000/api/v1/statpulse/leaderboard

# API documentation
open http://localhost:8000/api/docs
```

## 🗄️ Database

```bash
# Connect to PostgreSQL
psql postgresql://nexus:nexus_password@localhost:5432/nexus_football

# View tables
\dt

# Backup database
pg_dump nexus_football > backup.sql

# Restore database
psql nexus_football < backup.sql
```

## 📊 Monitoring

```bash
# View container logs
docker logs -f nexus-backend

# Monitor resource usage
docker stats

# Check container health
docker ps

# View network connections
docker network ls
```

## 🔐 Environment Setup

```bash
# Copy template
cp .env.example .env

# Edit with your keys
nano .env

# Required keys:
# ANTHROPIC_API_KEY
# OPENAI_API_KEY
# TOGETHER_API_KEY
# DATABASE_URL
# REDIS_URL
```

## 🧹 Cleanup

```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune

# Clean everything (careful!)
docker system prune -a
```

## 📚 Documentation

```bash
# View in terminal
cat README.md
cat QUICKSTART.md
cat DEPLOYMENT.md
cat FEATURES.md
cat PROJECT_SUMMARY.txt

# Or open in editor
code README.md
```

## 🆘 Troubleshooting

```bash
# Port already in use
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9

# Clear Docker cache
docker builder prune

# Reset everything
docker-compose down -v
git clean -fd
git reset --hard
```

## 💡 Useful Shortcuts

```bash
# Quick setup
docker-compose up -d && echo "Ready at http://localhost:3000"

# Quick test
pytest backend/tests -q && echo "All tests passed ✅"

# Quick push
git add . && git commit -m "wip" && git push

# Quick status
git status && docker ps && curl http://localhost:8000/health
```

---

For more details, see:
- **QUICKSTART.md** — Setup guide
- **DEPLOYMENT.md** — Production deployment
- **FEATURES.md** — Feature roadmap
- **GITHUB_PUSH.md** — GitHub push instructions
