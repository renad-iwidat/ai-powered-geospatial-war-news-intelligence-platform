# 🐳 Docker Deployment Review - GeoNews AI

## ⏰ Review Date: 2026-03-06

---

## ✅ WHAT'S WORKING CORRECTLY

### 1. Backend Dockerfile ✅
- Python 3.11-slim base image
- CAMeL Tools data download configured
- Non-root user setup
- Health check configured
- Port 8000 exposed

### 2. Frontend Dockerfile ✅
- Multi-stage build (deps → builder → runner)
- Node 20 Alpine
- Standalone output configured in next.config.ts
- Non-root user (nextjs)
- Port 3000 exposed

### 3. Docker Compose Structure ✅
- PostgreSQL with health check
- Backend service with dependencies
- Frontend service
- Processor service for batch processing
- Network configuration
- Volume for database persistence

### 4. Processing Scripts ✅
- `process_all_data.py` exists and works
- `generate_ai_forecasts.py` exists and works
- Both have proper error handling and logging

### 5. Environment Configuration ✅
- `.env` file has all required variables
- OPENAI_MODEL set to gpt-4o ✅
- Database URL configured

---

## ⚠️ CRITICAL ISSUES FOUND

### 🔴 ISSUE 1: Missing AI Forecast Cron Job in Docker Compose
**Problem**: The docker-compose.yml has a processor service that runs every 15 minutes, but there's NO service for generating AI forecasts twice daily (1 PM & 9 PM Palestine time).

**Current State**:
- Processor runs: `process_all_data.py` every 15 minutes ✅
- AI Forecast: ❌ NOT CONFIGURED

**Impact**: AI forecasts won't be generated automatically in Docker deployment.

**Solution**: Add a separate service for AI forecast generation.

---

### 🟡 ISSUE 2: Processor Service Uses Wrong Script
**Problem**: The processor service in docker-compose runs `process_all_data.py` which processes ALL unprocessed data (up to 15 batches). This could take a long time and block the next run.

**Current**:
```yaml
command: >
  sh -c "
    while true; do
      echo '[Processor] Running at $(date)'
      python scripts/process_all_data.py  # ← Processes everything!
      echo '[Processor] Completed. Next run in 15 minutes...'
      sleep 900
    done
  "
```

**Better Approach**: Use `process_batch.py` which processes only 1 small batch (10 news + 20 events) and completes quickly.

---

### 🟡 ISSUE 3: Environment Variables Not Passed to Processor
**Problem**: The processor service doesn't have `OPENAI_API_KEY` in environment variables, but it might be needed by some processing functions.

**Current**:
```yaml
processor:
  environment:
    DATABASE_URL: ...
    # Missing: OPENAI_API_KEY
```

---

### 🟡 ISSUE 4: Frontend Environment Variable
**Problem**: Frontend needs `NEXT_PUBLIC_API_URL` to connect to backend, but it's not set in docker-compose.

**Current**:
```yaml
frontend:
  environment:
    NEXT_PUBLIC_API_URL: ${NEXT_PUBLIC_API_URL:-http://localhost:8000}
```

**Issue**: In Docker, the frontend should connect to `http://backend:8000` (internal network), not `localhost`.

---

### 🟢 ISSUE 5: .dockerignore Excludes Important Scripts
**Problem**: The `.dockerignore` file excludes many scripts including test scripts, but keeps the important ones. This is actually GOOD for reducing image size.

**Status**: ✅ This is fine, all necessary scripts are included.

---

## 🔧 RECOMMENDED FIXES

### Fix 1: Add AI Forecast Service to docker-compose.yml

Add this service after the processor service:

```yaml
  # AI Forecast Generator (runs twice daily: 1 PM & 9 PM Palestine time = 11 AM & 7 PM UTC)
  ai-forecast:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: geonews-ai-forecast
    restart: unless-stopped
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER:-geonews_user}:${POSTGRES_PASSWORD:-changeme}@postgres:5432/${POSTGRES_DB:-geonews_db}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      OPENAI_MODEL: ${OPENAI_MODEL:-gpt-4o}
    command: >
      sh -c "
        while true; do
          current_hour=$$(date -u +%H)
          current_minute=$$(date -u +%M)
          
          # Run at 11:00 UTC (1 PM Palestine) and 19:00 UTC (9 PM Palestine)
          if [ \"$$current_hour\" = \"11\" ] && [ \"$$current_minute\" -lt \"15\" ]; then
            echo '[AI Forecast] Running 1 PM forecast at $$(date)'
            python scripts/generate_ai_forecasts.py
            echo '[AI Forecast] Completed. Sleeping until next run...'
            sleep 3600
          elif [ \"$$current_hour\" = \"19\" ] && [ \"$$current_minute\" -lt \"15\" ]; then
            echo '[AI Forecast] Running 9 PM forecast at $$(date)'
            python scripts/generate_ai_forecasts.py
            echo '[AI Forecast] Completed. Sleeping until next run...'
            sleep 3600
          else
            sleep 300
          fi
        done
      "
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - geonews-network
    volumes:
      - ./scripts:/app/scripts:ro
```

---

### Fix 2: Update Processor to Use Batch Script

Change the processor command to:

```yaml
  processor:
    # ... (keep existing config)
    command: >
      sh -c "
        while true; do
          echo '[Processor] Running batch at $$(date)'
          python scripts/process_batch.py
          echo '[Processor] Completed. Next run in 15 minutes...'
          sleep 900
        done
      "
```

---

### Fix 3: Add OPENAI_API_KEY to Processor

Update processor environment:

```yaml
  processor:
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER:-geonews_user}:${POSTGRES_PASSWORD:-changeme}@postgres:5432/${POSTGRES_DB:-geonews_db}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
```

---

### Fix 4: Fix Frontend API URL

Update frontend environment:

```yaml
  frontend:
    environment:
      NEXT_PUBLIC_API_URL: http://backend:8000
```

---

## 📋 DEPLOYMENT CHECKLIST

### Before Deployment:
- [ ] Update docker-compose.yml with all fixes above
- [ ] Create `.env.docker` file with production values
- [ ] Test locally: `docker-compose up --build`
- [ ] Verify all services start successfully
- [ ] Check processor logs (should run every 15 min)
- [ ] Check AI forecast logs (should run at 11 AM & 7 PM UTC)
- [ ] Test frontend at http://localhost:3000
- [ ] Test backend at http://localhost:8000/health

### Environment Variables Needed:
```bash
# .env.docker
POSTGRES_DB=geonews_db
POSTGRES_USER=geonews_user
POSTGRES_PASSWORD=<strong-password>

OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o

CORS_ORIGINS=http://localhost:3000,http://frontend:3000
```

### On Server:
1. Copy all files to server
2. Copy `.env.docker` to `.env`
3. Run: `docker-compose up -d`
4. Check logs: `docker-compose logs -f`
5. Verify services: `docker-compose ps`

---

## 🎯 FINAL RECOMMENDATIONS

### 1. Use Docker Compose for Deployment ✅
Docker Compose is perfect for your use case. It handles:
- Database
- Backend API
- Frontend
- Batch processor (every 15 min)
- AI forecast generator (twice daily)

### 2. Monitoring
Add these commands to your server:

```bash
# Check all services
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f processor
docker-compose logs -f ai-forecast

# Restart a service
docker-compose restart backend

# Stop all
docker-compose down

# Start all
docker-compose up -d
```

### 3. Backup Strategy
```bash
# Backup database
docker exec geonews-db pg_dump -U geonews_user geonews_db > backup.sql

# Restore database
docker exec -i geonews-db psql -U geonews_user geonews_db < backup.sql
```

### 4. Updates
```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose up -d --build
```

---

## 📊 EXPECTED BEHAVIOR AFTER DEPLOYMENT

### Every 15 Minutes:
```
[Processor] Running batch at Thu Mar  6 14:00:00 UTC 2026
🔄 Processing locations (batch of 10)...
✅ Processed: 10 news, 5 events
🔄 Processing metrics (batch of 20)...
✅ Processed: 20 events, 8 metrics
[Processor] Completed. Next run in 15 minutes...
```

### At 11:00 AM UTC (1 PM Palestine):
```
[AI Forecast] Running 1 PM forecast at Thu Mar  6 11:00:00 UTC 2026
🤖 Generating AI Intelligence Forecast (7 days)...
   ✅ Forecast generated and stored (ID: 123)
   📈 Trend: de-escalating
   🎯 Confidence: 70%
📊 Generating AI Trend Analysis...
   ✅ Trend analysis stored (ID: 124)
[AI Forecast] Completed. Sleeping until next run...
```

### At 19:00 PM UTC (9 PM Palestine):
```
[AI Forecast] Running 9 PM forecast at Thu Mar  6 19:00:00 UTC 2026
🤖 Generating AI Intelligence Forecast (7 days)...
   ✅ Forecast generated and stored (ID: 125)
[AI Forecast] Completed. Sleeping until next run...
```

---

## ✅ SUMMARY

### What's Good:
- ✅ Dockerfiles are well-configured
- ✅ Multi-stage builds for optimization
- ✅ Health checks configured
- ✅ Non-root users for security
- ✅ Processing scripts work correctly
- ✅ Database persistence configured

### What Needs Fixing:
- 🔴 Add AI forecast service to docker-compose
- 🟡 Change processor to use batch script
- 🟡 Add OPENAI_API_KEY to processor
- 🟡 Fix frontend API URL for Docker network

### After Fixes:
- ✅ Complete automated pipeline
- ✅ Data processing every 15 minutes
- ✅ AI forecasts twice daily
- ✅ All services connected properly
- ✅ Ready for production deployment

---

**Status**: 🟡 NEEDS MINOR FIXES BEFORE DEPLOYMENT

**Estimated Fix Time**: 10 minutes

**Next Step**: Apply the fixes to docker-compose.yml and test locally

