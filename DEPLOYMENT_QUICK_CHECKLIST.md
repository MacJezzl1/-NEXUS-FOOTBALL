# DEPLOYMENT CHECKLIST — Manual Steps Required

## Status
- ✅ GitHub push completed
- ✅ Configuration files created (vercel.json, railway.json, DEPLOYMENT_VERCEL_RAILWAY.md)
- ⏳ **Manual deployment steps required** (need your Vercel & Railway accounts)

---

## Quick Deploy Commands

### Frontend to Vercel (5 min)
```bash
# Install Vercel CLI
npm i -g vercel

# Login with GitHub
vercel login

# Deploy from project root
cd /home/macjezzl/spawn/nexus-football
vercel --prod
```

### Backend to Railway (10 min)
1. Go to https://railway.app
2. Create new project
3. Add PostgreSQL service (copy DATABASE_URL)
4. Add Redis service (copy REDIS_URL)
5. Add GitHub repo service (select `-NEXUS-FOOTBALL`, branch `main`)
6. Configure environment variables (from `.env.example`)
7. Wait for auto-deployment (~2-3 min)

---

## What You'll Get

| Service | Status |
|---------|--------|
| Frontend URL | `https://nexus-football-xyz.vercel.app` |
| Backend URL | `https://project-prod-railway.app` |
| API Docs | `https://project-prod-railway.app/api/docs` |

---

## Next Steps

Would you like to:

1. **Go ahead with manual Vercel + Railway deployment** (I can guide you through it step-by-step)
2. **Skip deployment for now** and move to:
   - Task 3: API Integration (live data sources)
   - Task 4: Test Data (load historical World Cup data)
   - Task 5: Environment Setup (configure API keys)

Which would you prefer?
