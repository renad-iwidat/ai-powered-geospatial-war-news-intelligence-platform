# Docker Scheduler Configuration Summary

## ✅ What Was Fixed

### 1. Scheduler Port Configuration
- ✅ `scripts/run_scheduler.py` updated to use port 7235 (was 8000)
- ✅ Default API_BASE_URL changed from `http://localhost:8000` to `http://localhost:7235`

### 2. Docker Compose
- ✅ Added optional standalone scheduler service (commented out)
- ✅ Scheduler uses `API_BASE_URL=http://backend:7235` for internal communication
- ✅ Scheduler depends on backend service

### 3. Environment Variables
- ✅ Added `API_BASE_URL=http://backend:7235` to .env
- ✅ Updated .env.example with scheduler configuration

## 🔧 How It Works

### Default: Integrated Scheduler
The scheduler runs inside the backend container automatically.

```bash
docker-compose up -d
# Backend starts with integrated scheduler
```

**Scheduler runs:**
- Data Processing: Every 15 minutes
- AI Forecast: Every 10 hours

### Optional: Standalone Scheduler
Run scheduler in a separate container for better resource isolation.

**To enable:**
1. Uncomment scheduler service in docker-compose.yml
2. Run `docker-compose up -d`

```yaml
scheduler:
  build:
    context: .
    dockerfile: Dockerfile
  container_name: geonews-scheduler
  restart: unless-stopped
  environment:
    DATABASE_URL: ${DATABASE_URL}
    OPENAI_API_KEY: ${OPENAI_API_KEY}
    OPENAI_MODEL: ${OPENAI_MODEL}
    NEWS_VIEW_NAME: ${NEWS_VIEW_NAME}
    API_BASE_URL: http://backend:7235
  command: python scripts/run_scheduler.py
  depends_on:
    - backend
  networks:
    - geonews-network
```

## 📋 Files Modified

```
✅ scripts/run_scheduler.py      - Port 7235 (was 8000)
✅ docker-compose.yml            - Added optional scheduler service
✅ .env                           - Added API_BASE_URL
✅ .env.example                   - Added API_BASE_URL documentation
```

## 📚 Documentation Created

```
✅ SCHEDULER_DOCKER_GUIDE.md     - Comprehensive scheduler guide
✅ DOCKER_SCHEDULER_SUMMARY.md   - This file
```

## 🚀 Running the Application

### Quick Start
```bash
# Start with integrated scheduler (default)
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
```

### With Standalone Scheduler
```bash
# 1. Uncomment scheduler in docker-compose.yml
# 2. Start services
docker-compose up -d

# 3. Check both services
docker-compose ps

# 4. View scheduler logs
docker-compose logs -f scheduler
```

## 🧪 Testing Scheduler

### Check Scheduler is Running
```bash
# View backend logs (integrated scheduler)
docker-compose logs -f backend | grep "Scheduler"

# Or view standalone scheduler logs
docker-compose logs -f scheduler
```

### Expected Log Output
```
✅ Scheduler started successfully
📅 Jobs scheduled:
   - Data Processing: Every 15 minutes
   - AI Forecast: Every 10 hours
```

### Test API Endpoints
```bash
# Test backend health
curl http://localhost:7235/health

# Test data processing endpoint
curl -X POST http://localhost:7235/api/v1/data-processing/extract-locations \
  -H "Content-Type: application/json" \
  -d '{"batch_size": 50}'
```

## 🔍 Monitoring

### View Scheduler Logs
```bash
# Integrated scheduler (in backend)
docker-compose logs -f backend

# Standalone scheduler
docker-compose logs -f scheduler

# Filter for scheduler messages
docker-compose logs backend | grep "🔄\|✅\|❌"
```

### Check Job Execution
```bash
# View last 50 lines
docker-compose logs --tail=50 backend

# Follow in real-time
docker-compose logs -f --tail=20 backend
```

## 🛠️ Troubleshooting

### Scheduler Not Running
```bash
# Check backend is running
docker-compose ps backend

# Check backend logs
docker-compose logs backend

# Restart backend
docker-compose restart backend
```

### Jobs Not Executing
```bash
# Check API connectivity
docker-compose exec backend curl http://localhost:7235/health

# Check scheduler logs for errors
docker-compose logs backend | grep "ERROR\|❌"
```

### Database Connection Issues
```bash
# Test database from backend
docker-compose exec backend python -c "
import asyncpg
import asyncio
from app.core.config import settings

async def test():
    try:
        conn = await asyncpg.connect(settings.DATABASE_URL)
        result = await conn.fetchval('SELECT 1')
        print(f'✓ Database connected')
        await conn.close()
    except Exception as e:
        print(f'✗ Database error: {e}')

asyncio.run(test())
"
```

## 📊 Scheduler Jobs

### Data Processing (Every 15 minutes)
```
POST /api/v1/data-processing/extract-locations
POST /api/v1/data-processing/extract-metrics
```

**Tasks:**
- Extract locations from news articles
- Extract metrics from events

### AI Forecast (Every 10 hours)
```
GET /api/v1/predictions/intelligence-forecast
GET /api/v1/predictions/trend-analysis
```

**Tasks:**
- Generate intelligence forecast
- Generate trend analysis

## 🌐 Network Communication

### Inside Docker Network
- Backend: `http://backend:7235`
- Scheduler → Backend: `http://backend:7235`
- Frontend → Backend: `http://backend:7235`

### From Host Machine
- Frontend: `http://localhost:3001`
- Backend: `http://localhost:7235`

## ✨ Key Features

- ✅ Integrated scheduler (default)
- ✅ Optional standalone scheduler
- ✅ Configurable via environment variables
- ✅ Automatic job scheduling
- ✅ Graceful shutdown handling
- ✅ Comprehensive logging
- ✅ Error handling and recovery

## 📝 Environment Variables

```bash
# Required
DATABASE_URL=postgresql://...
OPENAI_API_KEY=sk-...

# Scheduler Configuration
API_BASE_URL=http://backend:7235

# Optional
OPENAI_MODEL=gpt-4o
NEWS_VIEW_NAME=vw_news_ar_feed
```

## 🎯 Recommendations

### Development
- Use integrated scheduler (simpler)
- Monitor logs: `docker-compose logs -f backend`

### Production
- Use standalone scheduler (better isolation)
- Set up log aggregation
- Monitor job execution times
- Alert on failures

### Scaling
- Multiple backend instances
- Single scheduler instance
- Load balancer for backend

## 📖 For More Information

See:
- **SCHEDULER_DOCKER_GUIDE.md** - Detailed scheduler guide
- **DOCKER_SETUP.md** - Docker setup guide
- **DOCKER_QUICKSTART.md** - Quick start guide

## ✅ Ready to Deploy

Your scheduler is now properly configured for Docker:

1. **Default**: Integrated scheduler in backend
2. **Optional**: Standalone scheduler in separate container
3. **Configuration**: All environment variables set
4. **Monitoring**: Logs available via docker-compose

Run `docker-compose up -d` to start!
