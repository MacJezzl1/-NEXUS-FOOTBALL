# ⚽ NEXUS FOOTBALL — Deployment Guide

Production-ready deployment instructions for AWS, Vercel, Railway, and Docker.

## 🚀 DEPLOYMENT OPTIONS

### Option 1: Vercel (Frontend) + Railway (Backend)

**Fastest & Easiest Option for beginners**

#### Frontend Deployment (Vercel)

1. **Connect GitHub Repository**
   ```
   https://vercel.com/import
   → Select your nexus-football repository
   ```

2. **Configure Environment**
   ```
   REACT_APP_API_URL = https://your-backend.railway.app
   REACT_APP_ENV = production
   ```

3. **Deploy**
   - Vercel auto-deploys on git push
   - Get instant SSL certificate
   - CDN globally distributed

#### Backend Deployment (Railway)

1. **Connect Repository**
   ```
   https://railway.app
   → Connect GitHub → Select nexus-football
   ```

2. **Add Services**
   - PostgreSQL database
   - Redis cache
   - Python application

3. **Set Environment Variables**
   ```
   DATABASE_URL = ${DATABASE_URL}
   REDIS_URL = ${REDIS_URL}
   ANTHROPIC_API_KEY = your_key
   OPENAI_API_KEY = your_key
   ```

4. **Deploy**
   ```bash
   railway up
   ```

---

### Option 2: AWS (Production-Grade)

**For scalable, enterprise deployment**

#### Prerequisites
```bash
aws configure
# Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
```

#### Deploy with CloudFormation

```bash
# Create stack
aws cloudformation create-stack \
  --stack-name nexus-football-prod \
  --template-body file://infrastructure/aws-cloudformation.json \
  --parameters ParameterKey=EnvironmentName,ParameterValue=production

# Monitor deployment
aws cloudformation describe-stack-events \
  --stack-name nexus-football-prod
```

#### Components Deployed
- **ECS Fargate**: Backend containerization
- **RDS PostgreSQL**: Managed database (Multi-AZ)
- **ElastiCache Redis**: Managed cache cluster
- **S3 + CloudFront**: Frontend CDN
- **CloudWatch**: Logging & monitoring
- **Application Load Balancer**: Load distribution

#### Scaling
```bash
# Scale ECS tasks
aws ecs update-service \
  --cluster nexus-football-cluster \
  --service backend \
  --desired-count 5
```

---

### Option 3: Docker Compose (Self-Hosted)

**For VPS/dedicated servers**

```bash
# On your server
git clone https://github.com/MacJezzl1/-NEXUS-FOOTBALL.git
cd nexus-football

# Set environment
cp .env.example .env
# Edit .env with production values

# Start with docker-compose
docker-compose -f docker-compose.yml up -d

# View logs
docker-compose logs -f backend
```

#### Using Nginx Reverse Proxy

```nginx
upstream backend {
    server backend:8000;
}

server {
    listen 80;
    server_name api.nexusfootball.com;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

### Option 4: Kubernetes (Advanced)

**For multi-region, highly available deployment**

```bash
# Create namespace
kubectl create namespace nexus-football

# Deploy manifests
kubectl apply -f infrastructure/k8s/postgres.yaml
kubectl apply -f infrastructure/k8s/redis.yaml
kubectl apply -f infrastructure/k8s/backend.yaml
kubectl apply -f infrastructure/k8s/frontend.yaml

# View deployment
kubectl get pods -n nexus-football
```

---

## 🔐 SSL/TLS Configuration

### Let's Encrypt (Free)

```bash
# Using Certbot
sudo certbot certonly --standalone -d api.nexusfootball.com
sudo certbot certonly --standalone -d nexusfootball.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

### AWS Certificate Manager (Free)

```bash
# Request certificate
aws acm request-certificate \
  --domain-name nexusfootball.com \
  --validation-method DNS
```

---

## 📊 Monitoring & Logging

### CloudWatch (AWS)
```bash
# View backend logs
aws logs tail /ecs/nexus-football-backend --follow
```

### Sentry (Error Tracking)
```python
# Configure in backend/main.py
import sentry_sdk

sentry_sdk.init(
    dsn="https://your-key@sentry.io/project-id",
    traces_sample_rate=1.0
)
```

### Datadog (APM)
```bash
# Install agent
DD_AGENT_MAJOR_VERSION=7 \
DD_API_KEY=your_key \
DD_SITE=datadoghq.com \
bash -c "$(curl -L https://s3.amazonaws.com/dd-agent/scripts/install_agent.sh)"
```

---

## 🗄️ Database Migrations

### Initial Setup
```bash
# Apply migrations
python backend/manage.py migrate

# Create superuser
python backend/manage.py createsuperuser

# Load initial data
python backend/manage.py loaddata fixtures/teams.json
python backend/manage.py loaddata fixtures/matches.json
```

### Backup & Recovery
```bash
# PostgreSQL backup
pg_dump nexus_football > backup.sql

# Restore
psql nexus_football < backup.sql

# AWS RDS snapshot
aws rds create-db-snapshot \
  --db-instance-identifier nexus-db-prod \
  --db-snapshot-identifier backup-$(date +%Y%m%d)
```

---

## 🚨 Health Checks

### Application Healthcheck
```bash
curl https://api.nexusfootball.com/health
# Returns: {"status": "healthy", "service": "NEXUS FOOTBALL"}
```

### Database Connection
```bash
curl https://api.nexusfootball.com/db/health
```

### Cache Connectivity
```bash
curl https://api.nexusfootball.com/cache/health
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions (Included)

Automatically:
- ✅ Runs tests on every push
- ✅ Builds Docker images
- ✅ Deploys to staging
- ✅ Deploys to production on main branch

View workflow: `.github/workflows/ci-cd.yml`

### Manual Deployment

```bash
# Build images
docker build -t nexus-football-backend ./backend
docker build -t nexus-football-frontend ./frontend

# Push to registry
docker tag nexus-football-backend:latest your-registry/nexus-football-backend:latest
docker push your-registry/nexus-football-backend:latest

# Deploy
docker run -d \
  --name nexus-backend \
  -p 8000:8000 \
  -e DATABASE_URL=... \
  your-registry/nexus-football-backend:latest
```

---

## 📈 Performance Optimization

### Frontend
```bash
# Build optimization
npm run build
# Check bundle size
npm run analyze

# Results stored in build/
```

### Backend
```bash
# Enable caching headers
# Configure Redis for query caching
# Use CDN for static files
```

### Database
```sql
-- Create indexes
CREATE INDEX idx_match_status ON matches(status);
CREATE INDEX idx_player_team ON players(team_id);
CREATE INDEX idx_rating_match ON player_match_ratings(match_id);
```

---

## 🆘 Troubleshooting

### Backend Won't Start
```bash
# Check logs
docker logs nexus-backend

# Verify environment variables
docker exec nexus-backend env | grep DATABASE_URL

# Test database connection
docker exec nexus-backend python -c "import psycopg2; psycopg2.connect(os.getenv('DATABASE_URL'))"
```

### Frontend Not Loading
```bash
# Check CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id YOUR_DISTRIBUTION_ID \
  --paths "/*"

# Verify S3 bucket
aws s3 ls s3://your-bucket/
```

### High Latency
```bash
# Monitor metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --start-time 2026-06-11T00:00:00Z \
  --end-time 2026-06-12T00:00:00Z \
  --period 300 \
  --statistics Average
```

---

## 🔒 Security Checklist

- [ ] Enable HTTPS/TLS
- [ ] Set strong database passwords
- [ ] Enable database backups
- [ ] Configure WAF rules
- [ ] Set up DDoS protection
- [ ] Enable CloudTrail logging
- [ ] Configure VPC security groups
- [ ] Rotate API keys regularly
- [ ] Enable 2FA for AWS/GitHub
- [ ] Run security scans

---

## 📞 Support

- 📖 Full documentation: README.md
- 🐛 Issues: github.com/MacJezzl1/-NEXUS-FOOTBALL/issues
- 💬 Discussions: github.com/MacJezzl1/-NEXUS-FOOTBALL/discussions

---

**⚽ NEXUS FOOTBALL — Deployed and Ready for World Cup 2026**
