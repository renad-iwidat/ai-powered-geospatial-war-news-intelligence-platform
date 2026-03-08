# Scheduler Deployment Guide

## Overview

الـ Scheduler container يشتغل فقط:
- **Data Processing**: استخراج الـ locations والـ metrics من الـ news
- **AI Analysis**: تحليل الـ trends والـ forecasts

## Files

- `Dockerfile.scheduler` - Dockerfile للـ scheduler
- `docker-compose.scheduler.yml` - Docker Compose للـ scheduler + backend

## Usage

### Option 1: Run Scheduler with Backend

```bash
# Start both scheduler and backend
docker-compose -f docker-compose.scheduler.yml up -d

# View logs
docker-compose -f docker-compose.scheduler.yml logs -f scheduler

# Stop
docker-compose -f docker-compose.scheduler.yml down
```

### Option 2: Run Scheduler Only (Backend already running)

```bash
# Build scheduler image
docker build -f Dockerfile.scheduler -t geonews-scheduler .

# Run scheduler container
docker run -d \
  --name geonews-scheduler \
  --network geonews-network \
  -e DATABASE_URL="postgresql://..." \
  -e OPENAI_API_KEY="sk-..." \
  -e OPENAI_MODEL="gpt-4o" \
  -e NEWS_VIEW_NAME="vw_news_ar_feed" \
  -e API_BASE_URL="http://backend:7235" \
  geonews-scheduler
```

### Option 3: Run Locally (Development)

```bash
# Set environment variables
export DATABASE_URL="postgresql://..."
export OPENAI_API_KEY="sk-..."
export API_BASE_URL="http://localhost:7235"

# Run scheduler
python scripts/run_scheduler.py
```

## Environment Variables

```bash
# Required
DATABASE_URL=postgresql://...          # Render database
OPENAI_API_KEY=sk-...                  # OpenAI API key
API_BASE_URL=http://backend:7235       # Backend API URL

# Optional
OPENAI_MODEL=gpt-4o                    # OpenAI model
NEWS_VIEW_NAME=vw_news_ar_feed         # Database view
```

## Scheduler Jobs

### Data Processing (Every 15 minutes)
- Extracts locations from news articles
- Extracts metrics from events
- Calls: `POST /api/v1/data-processing/extract-locations`
- Calls: `POST /api/v1/data-processing/extract-metrics`

### AI Analysis (Every 10 hours)
- Generates intelligence forecast
- Generates trend analysis
- Calls: `GET /api/v1/predictions/intelligence-forecast`
- Calls: `GET /api/v1/predictions/trend-analysis`

## Monitoring

### View Logs
```bash
docker-compose -f docker-compose.scheduler.yml logs -f scheduler
```

### Check Status
```bash
docker-compose -f docker-compose.scheduler.yml ps
```

### View Job Execution
```bash
# Filter for job messages
docker-compose -f docker-compose.scheduler.yml logs scheduler | grep "🔄\|✅\|❌"
```

## Troubleshooting

### Scheduler not connecting to backend
```bash
# Check backend is running
docker-compose -f docker-compose.scheduler.yml ps backend

# Check backend logs
docker-compose -f docker-compose.scheduler.yml logs backend

# Test connectivity
docker-compose -f docker-compose.scheduler.yml exec scheduler curl http://backend:7235/health
```

### Database connection fails
- Verify DATABASE_URL is correct
- Check Render database is accessible
- Ensure firewall allows connection

### Jobs not executing
- Check API_BASE_URL is correct
- Check backend is running and healthy
- Check scheduler logs for errors

## Performance

### Image Size
- Scheduler Image: ~2.5-3.5 GB (same as backend)

### Build Time
- ~10-15 minutes (downloading dependencies)

### Runtime
- Memory: ~500 MB - 1 GB
- CPU: Low (runs jobs periodically)

## Production Deployment

### Using Docker Compose
```bash
docker-compose -f docker-compose.scheduler.yml up -d
```

### Using Docker Swarm
```bash
docker stack deploy -c docker-compose.scheduler.yml geonews
```

### Using Kubernetes
```bash
# Create ConfigMap for environment variables
kubectl create configmap geonews-scheduler-config \
  --from-literal=DATABASE_URL="postgresql://..." \
  --from-literal=OPENAI_API_KEY="sk-..." \
  --from-literal=API_BASE_URL="http://backend:7235"

# Deploy scheduler pod
kubectl apply -f scheduler-deployment.yaml
```

## Scaling

### Multiple Scheduler Instances
```yaml
# docker-compose.scheduler.yml
services:
  scheduler-1:
    # ... same config
  scheduler-2:
    # ... same config
  scheduler-3:
    # ... same config
```

**Note**: Ensure scheduler jobs don't overlap by using different schedules or job locking.

## Integration with Main Application

### Full Stack
```bash
# Terminal 1: Run full application (API + Frontend)
docker-compose up -d

# Terminal 2: Run scheduler separately
docker-compose -f docker-compose.scheduler.yml up -d scheduler
```

### Scheduler Only
```bash
# Run scheduler without frontend
docker-compose -f docker-compose.scheduler.yml up -d
```

## Logs and Debugging

### Enable Debug Logging
```bash
# In .env
LOG_LEVEL=DEBUG

# Restart scheduler
docker-compose -f docker-compose.scheduler.yml restart scheduler
```

### View Detailed Logs
```bash
# Last 100 lines
docker-compose -f docker-compose.scheduler.yml logs --tail=100 scheduler

# Follow with timestamps
docker-compose -f docker-compose.scheduler.yml logs --timestamps -f scheduler

# Filter for errors
docker-compose -f docker-compose.scheduler.yml logs scheduler | grep "ERROR"
```

## Summary

- **Dockerfile.scheduler**: Scheduler-only image
- **docker-compose.scheduler.yml**: Scheduler + Backend compose file
- **Jobs**: Data Processing (15 min) + AI Analysis (10 hours)
- **Database**: Render (external)
- **API**: Calls backend endpoints

Ready to deploy!
