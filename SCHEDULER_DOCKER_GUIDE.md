# Scheduler Configuration for Docker

## Overview

The scheduler can run in two ways:

1. **Integrated** (Default): Runs inside the backend container
2. **Standalone**: Runs in a separate container

## Integrated Scheduler (Default)

The scheduler runs automatically when the backend starts.

```bash
# Start backend with integrated scheduler
docker-compose up -d backend
```

**Advantages:**
- Single container
- Simpler deployment
- Automatic startup with backend

**Disadvantages:**
- Scheduler and API share resources
- If backend restarts, scheduler restarts

## Standalone Scheduler

Run scheduler in a separate container for better resource isolation.

### Enable Standalone Scheduler

1. **Uncomment in docker-compose.yml:**

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

2. **Start all services:**

```bash
docker-compose up -d
```

**Advantages:**
- Separate resource allocation
- Independent restart policy
- Better monitoring
- Can scale independently

**Disadvantages:**
- Additional container
- More complex deployment

## Configuration

### Environment Variables

```bash
# For integrated scheduler (in backend)
# Uses default: http://localhost:7235

# For standalone scheduler
API_BASE_URL=http://backend:7235
```

### Scheduler Jobs

The scheduler runs two jobs:

1. **Data Processing** - Every 15 minutes
   - Extracts locations from news articles
   - Extracts metrics from events

2. **AI Forecast** - Every 10 hours
   - Generates intelligence forecast
   - Generates trend analysis

## Running Scheduler Locally

For development, run the scheduler locally:

```bash
# Set environment variables
export DATABASE_URL="postgresql://..."
export OPENAI_API_KEY="sk-..."
export API_BASE_URL="http://localhost:7235"

# Run scheduler
python scripts/run_scheduler.py
```

## Monitoring Scheduler

### View Logs

```bash
# Integrated scheduler (in backend logs)
docker-compose logs -f backend

# Standalone scheduler
docker-compose logs -f scheduler
```

### Check Scheduler Status

```bash
# Check if scheduler container is running
docker-compose ps scheduler

# View scheduler logs with timestamps
docker-compose logs --timestamps -f scheduler
```

### Monitor Jobs

The scheduler logs show:
- Job start/end times
- Processing counts
- Success/failure status
- Error messages

Example log output:
```
🔄 Starting data processing at 2024-03-07T10:30:00
  → Extracting locations from news articles...
  ✓ Locations extracted: 50 articles processed
  → Extracting metrics from events...
  ✓ Metrics extracted: 100 events processed
✅ Data processing completed at 2024-03-07T10:35:00
```

## Troubleshooting

### Scheduler not running

```bash
# Check if scheduler container exists
docker-compose ps scheduler

# Check scheduler logs
docker-compose logs scheduler

# Restart scheduler
docker-compose restart scheduler
```

### Jobs not executing

```bash
# Check backend is running
docker-compose ps backend

# Check API_BASE_URL is correct
docker-compose exec scheduler env | grep API_BASE_URL

# Test API connectivity
docker-compose exec scheduler curl http://backend:7235/health
```

### Database connection issues

```bash
# Test database connection from scheduler
docker-compose exec scheduler python -c "
import asyncpg
import asyncio
from app.core.config import settings

async def test():
    try:
        conn = await asyncpg.connect(settings.DATABASE_URL)
        result = await conn.fetchval('SELECT 1')
        print(f'✓ Database connected: {result}')
        await conn.close()
    except Exception as e:
        print(f'✗ Database error: {e}')

asyncio.run(test())
"
```

## Switching Between Modes

### From Integrated to Standalone

1. **Disable integrated scheduler in backend:**
   - Comment out scheduler start in app/main.py (optional)

2. **Enable standalone scheduler:**
   - Uncomment scheduler service in docker-compose.yml

3. **Restart services:**
   ```bash
   docker-compose down
   docker-compose up -d
   ```

### From Standalone to Integrated

1. **Comment out scheduler service in docker-compose.yml**

2. **Restart services:**
   ```bash
   docker-compose down
   docker-compose up -d
   ```

## Performance Considerations

### Integrated Scheduler
- CPU: Shared with API
- Memory: Shared with API
- Network: Local calls
- Latency: Minimal

### Standalone Scheduler
- CPU: Dedicated
- Memory: Dedicated
- Network: Docker network calls
- Latency: Slightly higher

## Production Recommendations

**For Production:**

1. **Use Standalone Scheduler** for:
   - Better resource isolation
   - Independent scaling
   - Easier monitoring
   - Separate restart policies

2. **Configuration:**
   ```bash
   # .env
   API_BASE_URL=http://backend:7235
   DATABASE_URL=postgresql://...
   OPENAI_API_KEY=sk-...
   ```

3. **Monitoring:**
   - Set up log aggregation
   - Monitor job execution times
   - Alert on job failures
   - Track API response times

4. **Scaling:**
   - Run multiple backend instances
   - Single scheduler instance
   - Use load balancer for backend

## Example: Production Setup

```yaml
services:
  backend:
    # Multiple instances for load balancing
    deploy:
      replicas: 3
    
  scheduler:
    # Single instance
    restart: unless-stopped
    depends_on:
      - backend
```

## API Endpoints for Scheduler

The scheduler calls these endpoints:

- `POST /api/v1/data-processing/extract-locations`
- `POST /api/v1/data-processing/extract-metrics`
- `GET /api/v1/predictions/intelligence-forecast`
- `GET /api/v1/predictions/trend-analysis`

Ensure these endpoints are available and working correctly.

## Logs and Debugging

### Enable Debug Logging

```bash
# In .env
LOG_LEVEL=DEBUG

# Restart services
docker-compose restart
```

### View Detailed Logs

```bash
# Last 100 lines
docker-compose logs --tail=100 scheduler

# Follow logs with timestamps
docker-compose logs --timestamps -f scheduler

# Filter logs
docker-compose logs scheduler | grep "ERROR"
```

## Summary

- **Default**: Integrated scheduler in backend
- **Optional**: Standalone scheduler in separate container
- **Configuration**: API_BASE_URL environment variable
- **Monitoring**: Check logs with `docker-compose logs`
- **Production**: Use standalone scheduler for better isolation
