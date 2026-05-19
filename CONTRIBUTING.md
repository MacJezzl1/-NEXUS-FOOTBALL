# Contributing to NEXUS FOOTBALL

We love contributions! Thank you for helping make the World Cup 2026 Intelligence Platform better.

## Getting Started

1. **Fork the repository**
2. **Clone your fork**: `git clone https://github.com/your-username/nexus-football.git`
3. **Create a feature branch**: `git checkout -b feature/amazing-feature`

## Setup Development Environment

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 14+
- Redis 7+

### Installation

```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install

# Start services
docker-compose up -d
```

## Development Workflow

### Branches
- `main` — Production-ready code
- `develop` — Development branch
- `feature/*` — Feature branches
- `bugfix/*` — Bug fix branches

### Commit Message Format

```
type(scope): subject

body

footer
```

**Types:**
- `feat` — New feature
- `fix` — Bug fix
- `docs` — Documentation
- `style` — Code style
- `refactor` — Refactoring
- `test` — Tests
- `chore` — Maintenance

**Example:**
```
feat(pitchoracle): add ensemble model weighting

Implement dynamic model weighting based on recent accuracy
to improve prediction confidence scores.

Closes #42
```

## Three Core Systems

### 🔵 PitchOracle
- Prediction ensemble in `backend/apis/pitchoracle.py`
- Feature engineering in `backend/services/predictor.py`
- Tests in `backend/tests/test_pitchoracle.py`

### 🟢 StatPulse
- Rating engine in `backend/apis/statpulse.py`
- Player scoring in `backend/services/rater.py`
- Tests in `backend/tests/test_statpulse.py`

### 🔴 MatchMind AI
- Report generation in `backend/apis/matchmind.py`
- AI orchestration in `backend/services/ai_engine.py`
- Prompt templates in `backend/prompts/`

## Code Style

### Python
- Follow PEP 8
- Use `black` for formatting: `black backend/`
- Use `ruff` for linting: `ruff check backend/`
- Type hints required

### JavaScript/React
- Use Prettier: `npm run format`
- Use ESLint: `npm run lint`
- 2-space indentation

## Testing

```bash
# Backend tests
pytest backend/tests -v --cov

# Frontend tests
npm test

# Integration tests
npm run test:integration
```

## Pull Request Process

1. Update the README.md with any new features
2. Update `CHANGELOG.md` with changes
3. Ensure all tests pass: `npm test` and `pytest`
4. Request review from maintainers
5. Merge when approved

## AI Model Integration

When adding new AI models:

1. Add to `AIEnsembleEngine.MODELS` dict
2. Implement in `backend/services/ai_engine.py`
3. Add tests
4. Update documentation
5. Test with sample matches

Example:
```python
'new_model': {
    'provider': 'provider_name',
    'capability': 'analysis_type'
}
```

## Data Sources

When using new data sources:

1. Add collector in `data/collectors/`
2. Update `DataPipelineOrchestrator`
3. Add error handling
4. Document source in README
5. Add tests

## Documentation

- Docstrings for all functions (Google style)
- Update README.md for user-facing changes
- Update API docs in FastAPI
- Add comments for complex logic

## Deployment

### Local Testing
```bash
docker-compose up
# Visit http://localhost:3000
```

### Production
- Use Railway or Vercel for deployment
- Set environment variables
- Run migrations
- Monitor with Sentry

## Questions?

- Check existing issues
- Read the documentation
- Ask in discussions
- Email: dev@nexusfootball.com

## License

MIT — See LICENSE file

---

**Thank you for contributing to NEXUS FOOTBALL!** ⚽
