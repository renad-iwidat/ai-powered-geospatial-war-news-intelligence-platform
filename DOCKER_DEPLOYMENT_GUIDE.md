# 🐳 Docker Deployment Guide - GeoNews AI

## 📋 Prerequisites

### On Your Server:
- Docker installed (version 20.10+)
- Docker Compose installed (version 2.0+)
- Git installed
- At least 2GB RAM available
- At least 10GB disk space

### Check Installation:
```bash
docker --version
docker-compose --version
git --version
```

---

## 🚀 Step-by-Step Deployment

### Step 1: Clone Repository
```bash
# Clone your repository
git clone <your-repo-url> geonews-ai
cd geonews-ai
```

### Step 2: Configure Environment Variables
```bash
# Copy the Docker environment template
cp .env.docker .env

# Edit the .env file with your values
nano .env
```

**Required Changes in .env:**
```bash
# Change this to a strong password
POSTGRES_PASSWORD=your_strong_password_here

# Add your OpenAI API key
OPENAI_API_KEY=sk-proj-your_actual_key_here

# Keep this as is (GPT-4o model)
OPENAI_MODEL=gpt-4o

# For production, set your domain
CORS_ORIGINS=https://yourdomain.com
```

### Step 3: Build and Start Services
```bash
# Build all Docker images (first time only, takes 5-10 minutes)
docker-compose build

# Start all services in background
docker-compose up -d

# View logs to ensure everything started correctly
docker-compose logs -f
```

**Expected Output:**
```
✅ geonews-db         | database system is ready to accept connections
✅ geonews-backend    | Application startup complete
✅ geonews-frontend   | ready - started server on 0.0.0.0:3000
✅ geonews-processor  | [Processor] Running batch at ...
✅ geonews-ai-forecast| [AI Forecast] Waiting for scheduled time...
```

### Step 4: Verify Services
```bash
# Check all services are running
docker-compose ps

# Should show:
# NAME                  STATUS    PORTS
# geonews-db            Up        0.0.0.0:5432->5432/tcp
# geonews-backend       Up        0.0.0.0:8000->8000/tcp
# geonews-frontend      Up        0.0.0.0:3000->3000/tcp
# geonews-processor     Up
# geonews-ai-forecast   Up
```

### Step 5: Test the Application

**Test Backend API:**
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy","database":"connected","version":"1.0.0"}

curl http://localhost:8000/api/v1/news-articles?limit=5
# Expected: JSON array of news articles
```

**Test Frontend:**
```bash
# Open in browser
http://localhost:3000

# Or test with curl
curl http://localhost:3000
# Expected: HTML content
```

### Step 6: Run Database Migration (First Time Only)
```bash
# Enter the backend container
docker exec -it geonews-backend bash

# Run migration to create ai_forecasts table
python scripts/run_migration.py scripts/migrations/001_create_ai_forecasts_table.sql

# Exit container
exit
```

### Step 7: Generate Initial AI Forecasts
```bash
# Generate first set of forecasts manually
docker exec geonews-backend python scripts/generate_ai_forecasts.py

# Check if forecasts were created
docker exec geonews-db psql -U geonews_user -d geonews_db -c "SELECT COUNT(*) FROM ai_forecasts;"
```

---

## 📊 Monitoring Services

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f processor
docker-compose logs -f ai-forecast
docker-compose logs -f frontend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Check Service Status
```bash
# List all services
docker-compose ps

# Check resource usage
docker stats

# Check specific container
docker inspect geonews-backend
```

### Restart Services
```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart backend
docker-compose restart processor
```

---

## 🔄 Automated Processing Schedule

### Data Processor (Every 15 Minutes)
```
00:00 → Process batch (10 news + 20 events)
00:15 → Process batch
00:30 → Process batch
00:45 → Process batch
01:00 → Process batch
... continues 24/7
```

**What it does:**
- Extracts locations from 10 news articles
- Geocodes place names to coordinates
- Creates events
- Extracts metrics from 20 events
- Stores in database

**Check logs:**
```bash
docker-compose logs -f processor
```

### AI Forecast Generator (Twice Daily)
```
11:00 UTC (1 PM Palestine) → Generate forecasts
19:00 UTC (9 PM Palestine) → Generate forecasts
```

**What it does:**
- Generates 7-day intelligence forecast
- Generates trend analysis
- Caches results for 8 hours
- All API calls read from cache

**Check logs:**
```bash
docker-compose logs -f ai-forecast
```

---

## 🛠️ Maintenance Commands

### Update Application
```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose up -d --build

# Check logs
docker-compose logs -f
```

### Backup Database
```bash
# Create backup
docker exec geonews-db pg_dump -U geonews_user geonews_db > backup_$(date +%Y%m%d).sql

# Compress backup
gzip backup_$(date +%Y%m%d).sql
```

### Restore Database
```bash
# Stop services
docker-compose stop backend processor ai-forecast

# Restore from backup
gunzip -c backup_20260306.sql.gz | docker exec -i geonews-db psql -U geonews_user geonews_db

# Start services
docker-compose start backend processor ai-forecast
```

### Clean Up Old Data
```bash
# Enter database
docker exec -it geonews-db psql -U geonews_user geonews_db

# Delete old forecasts (older than 7 days)
DELETE FROM ai_forecasts WHERE generated_at < NOW() - INTERVAL '7 days';

# Exit
\q
```

### View Database
```bash
# Enter database shell
docker exec -it geonews-db psql -U geonews_user geonews_db

# Useful queries:
\dt                          # List tables
SELECT COUNT(*) FROM raw_news;
SELECT COUNT(*) FROM news_events;
SELECT COUNT(*) FROM event_metrics;
SELECT COUNT(*) FROM ai_forecasts;

# Check processing status
SELECT 
  COUNT(*) as total_news,
  COUNT(DISTINCT ne.raw_news_id) as with_events,
  ROUND(COUNT(DISTINCT ne.raw_news_id)::numeric / COUNT(*)::numeric * 100, 1) as completion_pct
FROM raw_news rn
LEFT JOIN news_events ne ON rn.id = ne.raw_news_id;

# Exit
\q
```

---

## 🚨 Troubleshooting

### Service Won't Start

**Check logs:**
```bash
docker-compose logs backend
```

**Common issues:**
1. Database not ready → Wait 30 seconds and check again
2. Port already in use → Change port in docker-compose.yml
3. Environment variable missing → Check .env file

### Database Connection Failed

**Check database is running:**
```bash
docker-compose ps postgres
```

**Test connection:**
```bash
docker exec geonews-db psql -U geonews_user -d geonews_db -c "SELECT 1;"
```

**Restart database:**
```bash
docker-compose restart postgres
```

### Frontend Can't Connect to Backend

**Check backend is running:**
```bash
curl http://localhost:8000/health
```

**Check frontend environment:**
```bash
docker exec geonews-frontend env | grep NEXT_PUBLIC_API_URL
# Should show: NEXT_PUBLIC_API_URL=http://backend:8000
```

**Restart frontend:**
```bash
docker-compose restart frontend
```

### Processor Not Running

**Check logs:**
```bash
docker-compose logs -f processor
```

**Manually run processing:**
```bash
docker exec geonews-backend python scripts/process_batch.py
```

### AI Forecasts Not Generating

**Check OpenAI API key:**
```bash
docker exec geonews-backend env | grep OPENAI_API_KEY
```

**Manually generate forecast:**
```bash
docker exec geonews-backend python scripts/generate_ai_forecasts.py
```

**Check forecast schedule:**
```bash
# AI forecasts run at 11:00 and 19:00 UTC
# Check current time
date -u
```

---

## 🔒 Security Recommendations

### 1. Change Default Passwords
```bash
# In .env file
POSTGRES_PASSWORD=use_a_very_strong_password_here
```

### 2. Restrict CORS Origins
```bash
# In .env file
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 3. Use Firewall
```bash
# Only allow necessary ports
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

### 4. Regular Updates
```bash
# Update Docker images monthly
docker-compose pull
docker-compose up -d
```

### 5. Backup Regularly
```bash
# Add to crontab (daily backup at 2 AM)
0 2 * * * cd /path/to/geonews-ai && docker exec geonews-db pg_dump -U geonews_user geonews_db | gzip > /backups/geonews_$(date +\%Y\%m\%d).sql.gz
```

---

## 📈 Performance Optimization

### 1. Increase Database Resources
```yaml
# In docker-compose.yml, add to postgres service:
command: postgres -c shared_buffers=256MB -c max_connections=100
```

### 2. Limit Processor Batch Size
```bash
# Edit scripts/process_batch.py
# Reduce batch_size if processing is slow
```

### 3. Monitor Resource Usage
```bash
# Check CPU and memory
docker stats

# If high usage, consider:
# - Increasing server resources
# - Reducing batch sizes
# - Increasing sleep intervals
```

---

## 🌐 Production Deployment with Domain

### 1. Setup Reverse Proxy (Nginx)

**Install Nginx:**
```bash
sudo apt update
sudo apt install nginx
```

**Configure Nginx:**
```bash
sudo nano /etc/nginx/sites-available/geonews
```

**Add configuration:**
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check
    location /health {
        proxy_pass http://localhost:8000/health;
    }
}
```

**Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/geonews /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 2. Setup SSL with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal is configured automatically
```

### 3. Update Environment Variables

```bash
# In .env file
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

```bash
# Restart services
docker-compose restart
```

---

## ✅ Deployment Checklist

Before going live:

- [ ] Server has Docker and Docker Compose installed
- [ ] .env file configured with strong passwords
- [ ] OpenAI API key added to .env
- [ ] All services start successfully: `docker-compose ps`
- [ ] Backend health check passes: `curl http://localhost:8000/health`
- [ ] Frontend loads: `curl http://localhost:3000`
- [ ] Database migration completed
- [ ] Initial AI forecasts generated
- [ ] Processor logs show batch processing every 15 minutes
- [ ] AI forecast logs show scheduled runs at 11:00 and 19:00 UTC
- [ ] Nginx configured (if using domain)
- [ ] SSL certificate installed (if using domain)
- [ ] Firewall configured
- [ ] Backup cron job configured

---

## 📞 Support

### Check System Status
```bash
# Quick health check
docker-compose ps
curl http://localhost:8000/health
curl http://localhost:3000

# View recent logs
docker-compose logs --tail=50 backend
docker-compose logs --tail=50 processor
```

### Common Commands Reference
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart all services
docker-compose restart

# View logs
docker-compose logs -f

# Update application
git pull && docker-compose up -d --build

# Backup database
docker exec geonews-db pg_dump -U geonews_user geonews_db > backup.sql

# Enter database
docker exec -it geonews-db psql -U geonews_user geonews_db
```

---

**Last Updated**: 2026-03-06  
**Version**: 1.0.0  
**Status**: Production Ready ✅

