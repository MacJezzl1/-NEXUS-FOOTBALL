# ENVIRONMENT SETUP & API KEYS CONFIGURATION

This guide walks you through obtaining and configuring all necessary API keys and secrets for production deployment.

**Timeline:** 20-30 minutes

---

## Required API Keys Summary

| Service | Purpose | Free Tier | Cost | Urgency |
|---------|---------|-----------|------|---------|
| **Anthropic** | Claude AI models | 3 months trial | $0.003/1k tokens | High |
| **OpenAI** | GPT-4 for analysis | $5/month | $0.03/1k tokens | High |
| **Together AI** | Ensemble model backend | 1M tokens free | Pay-as-you-go | Medium |
| **Cohere** | Text analysis | 100k tokens/month | $0.50/1M tokens | Medium |
| **RapidAPI (API-Football)** | Live match data | 500 req/month | $9.99+/month | High |
| **football-data.org** | Fixtures & standings | 10 req/min | $9.99+/month | Medium |
| **Sentry** | Error monitoring | 5k events/month | $29+/month | Low |

---

## Step 1: AI Model API Keys (PitchOracle & MatchMind)

### 1.1 Anthropic (Claude)

1. **Get API Key:**
   - Go to https://console.anthropic.com
   - Sign up / Log in
   - Click "API Keys" → "Create Key"
   - Copy your key

2. **Usage:**
   - PitchOracle: Win/draw/loss predictions
   - MatchMind: Detailed match analysis reports
   - Budget: ~$10-20/month for testing

3. **Add to .env:**
   ```
   ANTHROPIC_API_KEY=sk-ant-XXXXXXXXXXXXXXXXXXXX
   ```

---

### 1.2 OpenAI (GPT-4)

1. **Get API Key:**
   - Go to https://platform.openai.com
   - Sign up / Log in
   - Click "API Keys" → "Create new secret key"
   - Copy your key

2. **Usage:**
   - Team analysis
   - Player statistical summaries
   - AI report generation
   - Budget: ~$10-15/month

3. **Add to .env:**
   ```
   OPENAI_API_KEY=sk-XXXXXXXXXXXXXXXXXX
   ```

---

### 1.3 Together AI

1. **Get API Key:**
   - Go to https://www.together.ai
   - Sign up / Log in
   - Dashboard → API Keys
   - Copy your key

2. **Usage:**
   - Open-source model ensemble (Llama, Mistral)
   - Cost-effective alternative to GPT-4
   - Budget: Free tier usually sufficient for testing

3. **Add to .env:**
   ```
   TOGETHER_API_KEY=xxxxxxxxxxxxxxxxxxxxx
   ```

---

### 1.4 Cohere

1. **Get API Key:**
   - Go to https://dashboard.cohere.com
   - Sign up / Log in
   - API Keys → Create new key
   - Copy your key

2. **Usage:**
   - Text generation for reports
   - Semantic similarity for player comparisons
   - Budget: Free tier (100k tokens/month) usually sufficient

3. **Add to .env:**
   ```
   COHERE_API_KEY=xxxxxxxxxxxxxxxxxxxxx
   ```

---

## Step 2: Football Data API Keys

### 2.1 RapidAPI (API-Football)

1. **Get API Key:**
   - Go to https://rapidapi.com/api-sports/api/api-football
   - Sign up with GitHub
   - Click "Subscribe to Free" (500 req/month)
   - Go to "Endpoints" → copy "x-rapidapi-key"

2. **Usage:**
   - Live match events
   - Team lineups and formations
   - Match statistics
   - Budget: Free tier = 500 req/month (~17/day)

3. **Performance Tip:**
   - Cache responses in Redis for 5+ minutes
   - Reduces API calls by 80%+
   - Use free tier comfortably

4. **Add to .env:**
   ```
   RAPIDAPI_KEY=xxxxxxxxxxxxxxxxxxxxxxx
   ```

---

### 2.2 football-data.org

1. **Get API Key:**
   - Go to https://www.football-data.org/client/register
   - Create account
   - Go to Profile → API Token
   - Copy your token

2. **Usage:**
   - All 104 World Cup 2026 fixtures
   - Match results and standings
   - Head-to-head records
   - Budget: Free tier = 10 req/min

3. **Add to .env:**
   ```
   FOOTBALL_DATA_KEY=xxxxxxxxxxxxxxxxxxxxxxx
   ```

---

## Step 3: Monitoring & Security

### 3.1 Sentry (Error Monitoring)

1. **Get DSN:**
   - Go to https://sentry.io
   - Sign up / Log in
   - Create new project → Python
   - Copy DSN

2. **Usage:**
   - Monitor errors in production
   - Track API failures
   - Budget: Free tier (5k errors/month)

3. **Add to .env:**
   ```
   SENTRY_DSN=https://xxxxxxx@sentry.io/xxxxxxx
   ```

---

## Step 4: Local Environment Setup

### 4.1 Create .env File

```bash
cd /home/macjezzl/spawn/nexus-football

# Create from template
cp .env.example .env

# Edit with your API keys
nano .env
```

### 4.2 Final .env File

```env
# ━━━━━ AI MODELS ━━━━━
ANTHROPIC_API_KEY=sk-ant-XXXXXXXXXXXXXXXXXXXX
OPENAI_API_KEY=sk-XXXXXXXXXXXXXXXXXX
TOGETHER_API_KEY=xxxxxxxxxxxxxxxxxxxxx
COHERE_API_KEY=xxxxxxxxxxxxxxxxxxxxx

# ━━━━━ FOOTBALL DATA ━━━━━
RAPIDAPI_KEY=xxxxxxxxxxxxxxxxxxxxxxx
FOOTBALL_DATA_KEY=xxxxxxxxxxxxxxxxxxxxxxx

# ━━━━━ DATABASE ━━━━━
DATABASE_URL=postgresql://nexus:password@localhost:5432/nexus_football
SUPABASE_URL=https://your-project.supabase.co  (optional)
SUPABASE_KEY=your_supabase_key  (optional)

# ━━━━━ REDIS ━━━━━
REDIS_URL=redis://localhost:6379

# ━━━━━ JWT & SECURITY ━━━━━
SECRET_KEY=your-256-char-random-string-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ━━━━━ ENVIRONMENT ━━━━━
ENV=production
DEBUG=false
LOG_LEVEL=INFO

# ━━━━━ CORS ━━━━━
CORS_ORIGINS=["https://your-vercel-frontend.vercel.app", "https://your-domain.com"]

# ━━━━━ MONITORING ━━━━━
SENTRY_DSN=https://xxxxxxx@sentry.io/xxxxxxx

# ━━━━━ FRONTEND ━━━━━
REACT_APP_API_URL=https://your-railway-backend.railway.app
REACT_APP_ENV=production
```

### 4.3 Generate Secret Key

```bash
# Generate 256-char random string for SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(256))"

# Copy output and paste into .env as SECRET_KEY
```

---

## Step 5: GitHub Repository Secrets

### 5.1 Add Secrets to GitHub

1. Go to GitHub repository settings:
   ```
   https://github.com/MacJezzl1/-NEXUS-FOOTBALL/settings/secrets/actions
   ```

2. Click "New repository secret" for each:
   ```
   ANTHROPIC_API_KEY
   OPENAI_API_KEY
   TOGETHER_API_KEY
   COHERE_API_KEY
   RAPIDAPI_KEY
   FOOTBALL_DATA_KEY
   DATABASE_URL (use test database for CI)
   REDIS_URL (use test Redis for CI)
   SECRET_KEY (different from production)
   SENTRY_DSN
   ```

3. Click "Add secret" for each one

### 5.2 Verify Secrets Added

```bash
# List all secrets (note: values are hidden)
gh secret list
```

---

## Step 6: Deployment Platform Configuration

### 6.1 Railway Backend Secrets

1. Go to https://railway.app
2. Select NEXUS FOOTBALL project → FastAPI service
3. Settings → Variables
4. Add all secrets from `.env.example`

**Note:** Railway environment variables override .env file

### 6.2 Vercel Frontend Configuration

1. Go to https://vercel.com/dashboard
2. Select `nexus-football` project
3. Settings → Environment Variables
4. Add:
   ```
   REACT_APP_API_URL=https://your-railway-backend.railway.app
   REACT_APP_ENV=production
   ```

---

## Step 7: Local Testing

### 7.1 Test API Keys (without deploying)

```bash
# Test Anthropic
python3 << 'EOF'
import anthropic
import os

api_key = os.getenv('ANTHROPIC_API_KEY')
client = anthropic.Anthropic(api_key=api_key)

message = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Test"}],
)
print(f"✓ Anthropic API working: {message.content[0].text[:50]}...")
EOF

# Test OpenAI
python3 << 'EOF'
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Test"}],
)
print(f"✓ OpenAI API working: {response.choices[0].message.content[:50]}...")
EOF

# Test API-Football
python3 << 'EOF'
import requests
import os

api_key = os.getenv('RAPIDAPI_KEY')
url = "https://api-football-v1.p.rapidapi.com/fixtures?live=all"
headers = {
    "x-rapidapi-key": api_key,
    "x-rapidapi-host": "api-football-v1.rapidapi.com"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    print(f"✓ API-Football working: {len(response.json().get('response', []))} matches")
else:
    print(f"✗ API-Football failed: {response.status_code}")
EOF
```

### 7.2 Test Data Pipeline

```bash
# Run data collection with all APIs
python -m data.collectors.data_pipeline

# Expected output:
# ✓ fbref: success (N records)
# ✓ statsbomb: success (N records)
# ✓ elo: success (N records)
# ✓ fifa: success (N records)
# ✓ api_football: success (N records)
# ✓ football_data: success (N records)
```

---

## Step 8: Production Deployment

### 8.1 Push to Main Branch

```bash
git add .env  # Don't commit .env!
git commit -m "chore: Add environment configuration"
git push origin main
```

**⚠️ IMPORTANT:** Never commit `.env` to GitHub. Use repository secrets instead.

### 8.2 Deploy to Railway

```bash
# Railway automatically deploys on push to main
# Monitor at: https://railway.app/project/[project-id]

# Check logs
railway logs
```

### 8.3 Deploy to Vercel

```bash
vercel --prod

# Environment variables already configured via dashboard
```

### 8.4 Verify Deployment

```bash
# Test backend API
curl https://your-railway-backend.railway.app/api/docs

# Test frontend
open https://nexus-football-xyz.vercel.app

# Test predictions
curl https://your-railway-backend.railway.app/api/v1/predictions
```

---

## Security Best Practices

✅ **DO:**
- Use environment variables for all secrets
- Rotate API keys every 90 days
- Use different keys for dev/staging/prod
- Monitor API key usage in dashboards
- Use GitHub repository secrets for CI/CD
- Enable API rate limiting
- Log API errors for debugging

❌ **DON'T:**
- Commit `.env` files to Git
- Use same API key for multiple environments
- Hardcode secrets in source code
- Share API keys in Slack/email
- Use old/expired API keys
- Disable SSL/TLS verification

---

## Monitoring & Alerts

### Check API Usage

```bash
# Anthropic: https://console.anthropic.com/usage
# OpenAI: https://platform.openai.com/account/usage
# RapidAPI: https://rapidapi.com/developer/dashboard
# Sentry: https://sentry.io
```

### Set Up Billing Alerts

- Anthropic: $15/month budget alert
- OpenAI: $10/month budget alert
- RapidAPI: Enable email notifications

---

## Troubleshooting

### Error: "Invalid API Key"
```
Solution: 
1. Verify key in .env or GitHub secret
2. Check you copied entire key (no spaces)
3. Ensure key hasn't been rotated/revoked
4. Try regenerating key in API dashboard
```

### Error: "Rate limit exceeded"
```
Solution:
1. Check free tier limits (see table above)
2. Enable Redis caching to reduce calls
3. Upgrade to paid tier
4. Distribute calls over time (queue system)
```

### Error: "Connection timeout"
```
Solution:
1. Verify internet connection
2. Check API service status page
3. Increase timeout in code (default 30s)
4. Try again - may be temporary outage
```

---

## Next Steps

1. ✅ Obtain all API keys (this task)
2. ✅ Configure .env locally
3. ✅ Add GitHub repository secrets
4. ✅ Configure Railway/Vercel environment
5. 🚀 Deploy and test in production
6. 📊 Monitor API usage and errors
7. 🔄 Set up continuous data collection
8. 📈 Launch public beta (May 2026)

