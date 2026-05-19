# DEPLOYMENT GUIDE — Vercel + Railway

This guide walks you through deploying NEXUS FOOTBALL frontend to Vercel and backend to Railway.

**Timeline:** ~15-20 minutes total

---

## Part 1: Vercel Frontend Deployment (5 minutes)

### Prerequisites
- GitHub account with `-NEXUS-FOOTBALL` repository
- Vercel account (free at https://vercel.com)

### Steps

1. **Login to Vercel**
   ```bash
   npm i -g vercel
   vercel login
   ```

2. **Deploy**
   ```bash
   cd /home/macjezzl/spawn/nexus-football
   vercel --prod
   ```
   - Select "Link to existing project?" → **NO** (create new)
   - Project name: `nexus-football`
   - Framework: **Other**
   - Root directory: `./`

3. **Configure Environment Variables in Vercel Dashboard**
   - Go to https://vercel.com/dashboard
   - Select `nexus-football` project
   - Settings → Environment Variables
   - Add these:
     ```
     REACT_APP_API_URL = https://<railway-backend-url> (update after Railway setup)
     REACT_APP_ENV = production
     ```

4. **Redeploy after adding env vars**
   ```bash
   vercel --prod
   ```

**Result:** Frontend deployed at `https://nexus-football-<random>.vercel.app`

---

## Part 2: Railway Backend Deployment (10-15 minutes)

### Prerequisites
- GitHub account with `-NEXUS-FOOTBALL` repository
- Railway account (free at https://railway.app)

### Steps

1. **Login to Railway**
   - Go to https://railway.app
   - Sign up / Log in with GitHub
   - Create new project

2. **Add Services to Railway Project**

   **2.1 PostgreSQL Database**
   - Click "+ Add Service" → Add from marketplace
   - Select PostgreSQL
   - Configure:
     - Postgres User: `nexus`
     - Postgres Password: (Railway generates one)
     - Database: `nexus_football`
   - Copy the `DATABASE_URL` connection string

   **2.2 Redis Cache**
   - Click "+ Add Service" → Add from marketplace
   - Select Redis
   - Default settings are fine
   - Copy the `REDIS_URL` connection string

   **2.3 FastAPI Backend**
   - Click "+ Add Service" → GitHub repo
   - Select `-NEXUS-FOOTBALL` repository
   - Branch: `main`
   - Root directory: `backend`
   - Auto-deploy on push: ✓ enabled

3. **Configure Backend Environment Variables**
   - Go to FastAPI service settings → Variables
   - Add all from `.env.example`:
     ```
     ANTHROPIC_API_KEY=<your-key>
     OPENAI_API_KEY=<your-key>
     TOGETHER_API_KEY=<your-key>
     COHERE_API_KEY=<your-key>
     RAPIDAPI_KEY=<your-key>
     SECRET_KEY=<generate-random-256-char-string>
     DATABASE_URL=<from-postgres-service>
     REDIS_URL=<from-redis-service>
     ENV=production
     DEBUG=false
     LOG_LEVEL=INFO
     ```

4. **Railway Auto-Deploys**
   - Backend automatically deploys from `main` branch
   - Monitor at https://railway.app
   - Once deployed, copy the public URL (e.g., `https://backend-prod.railway.app`)

5. **Update Vercel with Backend URL**
   - Go back to Vercel dashboard
   - Settings → Environment Variables
   - Update `REACT_APP_API_URL` = `https://backend-prod.railway.app`
   - Redeploy: `vercel --prod`

---

## Part 3: Configure Repository Secrets for CI/CD

Go to GitHub → Settings → Secrets and variables → Actions

Add these secrets:
```
ANTHROPIC_API_KEY
OPENAI_API_KEY
TOGETHER_API_KEY
COHERE_API_KEY
RAPIDAPI_KEY
DATABASE_URL (test database for CI)
REDIS_URL (test Redis for CI)
```

This enables GitHub Actions CI/CD to run tests automatically on each push.

---

## Deployment Checklist

- [ ] Vercel frontend deployed
- [ ] Railway PostgreSQL created
- [ ] Railway Redis created
- [ ] Railway FastAPI backend deployed
- [ ] Environment variables configured in Railway
- [ ] Backend API accessible at public URL
- [ ] Frontend updated with backend URL
- [ ] Frontend redeployed on Vercel
- [ ] GitHub repository secrets configured
- [ ] Test health endpoint: `GET <backend-url>/health`
- [ ] Test API docs: `GET <backend-url>/api/docs`

---

## URLs After Deployment

| Service | URL |
|---------|-----|
| Frontend | `https://nexus-football-<random>.vercel.app` |
| Backend API | `https://<project>-prod.railway.app` |
| API Documentation | `https://<project>-prod.railway.app/api/docs` |
| Admin Dashboard | `https://nexus-football-<random>.vercel.app/admin` |

---

## Troubleshooting

### Backend deployment fails
- Check Railway logs: Project → Deployments → View logs
- Ensure `DATABASE_URL` and `REDIS_URL` are set
- Verify Python 3.11 compatibility

### Frontend can't reach backend
- Check `REACT_APP_API_URL` in Vercel environment
- Verify backend CORS allows Vercel domain
- Check frontend console for 404/CORS errors

### Database migrations not running
- SSH into Railway backend: `railway connect`
- Run manually: `alembic upgrade head`
- Or add migration to start command

---

## Next Steps

1. ✅ Push to GitHub (done)
2. ✅ Deploy frontend to Vercel (do this)
3. ✅ Deploy backend to Railway (do this)
4. 📝 Environment Setup - Configure API keys
5. 📡 API Integration - Set up live data sources
6. 📊 Test Data - Load World Cup historical data

