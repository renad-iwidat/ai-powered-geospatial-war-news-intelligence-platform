# Background Scheduler Setup

## Quick Start

### Option 1: Integrated Scheduler (Recommended)

The scheduler runs automatically with the FastAPI application:

```bash
# Install dependencies
pip install -r requirements.txt

# Start the application (scheduler runs in background)
uvicorn app.main:app --reload
```

You'll see in the logs:
```
✅ Scheduler started successfully
📅 Jobs scheduled:
   - Data Processing: Every 15 minutes
   - AI Forecast: Every 10 hours
```

### Option 2: Standalone Scheduler

Run the scheduler as a separate process:

```bash
# Install dependencies
pip install -r requirements.txt

# Run standalone scheduler
python scripts/run_scheduler.py
```

### Option 3: Docker Compose

```bash
# Start all services (API + Database + Scheduler)
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop all services
docker-compose down
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  FastAPI Application                    │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Background Scheduler (APScheduler + Threading)  │  │
│  │                                                   │  │
│  │  ┌──────────────────┐  ┌──────────────────────┐  │  │
│  │  │  Worker Thread 1 │  │  Worker Thread 2     │  │  │
│  │  │                  │  │                      │  │  │
│  │  │ Data Processing  │  │ AI Forecast          │  │  │
│  │  │ (Every 15 min)   │  │ (Every 10 hours)     │  │  │
│  │  │                  │  │                      │  │  │
│  │  │ • Locations      │  │ • Intelligence       │  │  │
│  │  │ • Metrics        │  │ • Trend Analysis     │  │  │
│  │  └──────────────────┘  └──────────────────────┘  │  │
│  │                                                   │  │
│  │  ✓ Parallel Execution                            │  │
│  │  ✓ No Overlapping (max_instances=1)              │  │
│  │  ✓ Automatic Retry on Failure                    │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Scheduled Tasks

### 1. Data Processing (Every 15 minutes)

**What it does:**
- Extracts geographic locations from news articles using NER
- Extracts numerical metrics (casualties, weapons, etc.) from events
- Updates database with processed data

**Configuration:**
- Location batch size: 50 articles
- Metrics batch size: 100 events
- Max instances: 1 (prevents overlapping)

**API Endpoints Called:**
```
POST /api/v1/data-processing/extract-locations
POST /api/v1/data-processing/extract-metrics
```

### 2. AI Forecast Generation (Every 10 hours)

**What it does:**
- Generates AI-powered intelligence forecasts using OpenAI GPT
- Analyzes geopolitical trends
- Updates cached forecasts for frontend

**Configuration:**
- Forecast days: 7
- Force refresh: true (bypass cache)
- Max instances: 1 (prevents overlapping)

**API Endpoints Called:**
```
GET /api/v1/predictions/intelligence-forecast?days=7&force_refresh=true
GET /api/v1/predictions/trend-analysis
```

## Parallel Execution Example

When both tasks are scheduled to run at the same time:

```
Timeline:
10:00 AM
├─ Data Processing starts (Thread 1)
│  └─ Extracting locations...
│  └─ Extracting metrics...
│  └─ Completed at 10:05 AM
│
├─ AI Forecast starts (Thread 2)  ← Parallel execution
│  └─ Generating intelligence forecast...
│  └─ Generating trend analysis...
│  └─ Completed at 10:15 AM
│
└─ Both tasks run simultaneously without blocking each other
```

## Monitoring

### Check Scheduler Status

View logs to see scheduler activity:

```bash
# If running with FastAPI
uvicorn app.main:app --reload

# If running standalone
python scripts/run_scheduler.py

# If running with Docker
docker-compose logs -f backend
```

### Example Log Output

```
✅ Scheduler started successfully
📅 Jobs scheduled:
   - Data Processing: Every 15 minutes
   - AI Forecast: Every 10 hours

🔄 Starting data processing at 2026-03-07T10:00:00
  → Extracting locations from news articles...
  ✓ Locations extracted: 45 articles processed
  → Extracting metrics from events...
  ✓ Metrics extracted: 120 events processed
✅ Data processing completed at 2026-03-07T10:05:30

🤖 Starting AI forecast generation at 2026-03-07T10:00:00
  → Generating intelligence forecast...
  ✓ Intelligence forecast generated
    Risk Level: high
    Confidence: 85%
  → Generating trend analysis...
  ✓ Trend analysis generated
    Overall Trend: escalating
    Trend Strength: 78%
✅ AI forecast generation completed at 2026-03-07T10:15:45
```

### Check Processing Status

```bash
curl http://localhost:8000/api/v1/data-processing/status
```

Response:
```json
{
  "total_articles": 5000,
  "articles_with_events": 4500,
  "articles_without_events": 500,
  "total_events": 8000,
  "events_with_metrics": 7200,
  "events_without_metrics": 800,
  "processing_completion_percentage": 87.5
}
```

## Configuration

### Adjust Schedule Intervals

Edit `app/services/scheduler.py`:

```python
# Change data processing interval
self.scheduler.add_job(
    self._run_data_processing,
    trigger=IntervalTrigger(minutes=15),  # ← Change this
    ...
)

# Change AI forecast interval
self.scheduler.add_job(
    self._run_ai_forecast,
    trigger=IntervalTrigger(hours=10),  # ← Change this
    ...
)
```

### Adjust Batch Sizes

Edit `app/services/scheduler.py`:

```python
# Location extraction batch size
json={"batch_size": 50}  # ← Change this

# Metrics extraction batch size
json={"batch_size": 100}  # ← Change this
```

### Adjust Worker Threads

Edit `app/services/scheduler.py`:

```python
self.scheduler = BackgroundScheduler(
    daemon=True,
    max_workers=2,  # ← Change this (default: 2)
    thread_pool_executor_kwargs={'max_workers': 2}
)
```

## Troubleshooting

### Scheduler Not Starting

**Error:** `ModuleNotFoundError: No module named 'apscheduler'`

**Solution:**
```bash
pip install apscheduler
```

### Tasks Not Running

**Check:**
1. Verify scheduler is running: Look for "✅ Scheduler started successfully"
2. Check API connectivity: `curl http://localhost:8000/health`
3. Check database: `curl http://localhost:8000/api/v1/data-processing/status`
4. Review logs for errors

### High CPU Usage

**Solutions:**
1. Increase interval times (e.g., 30 minutes instead of 15)
2. Reduce batch sizes
3. Check if tasks are completing successfully
4. Monitor database performance

### Memory Leaks

**Solutions:**
1. Ensure tasks complete successfully
2. Check for unclosed connections
3. Monitor database connection pool
4. Consider running scheduler in separate process

## Performance Tips

1. **Stagger Schedules**
   - Run data processing at :00, :15, :30, :45
   - Run AI forecast at 2 AM, 12 PM, 10 PM

2. **Optimize Batch Sizes**
   - Smaller batches = more frequent, less resource intensive
   - Larger batches = less frequent, more resource intensive

3. **Use Separate Process**
   - For production, run scheduler in separate container
   - Prevents scheduler from blocking API requests

4. **Monitor Resources**
   - Track CPU, memory, database connections
   - Use tools like htop, docker stats, or cloud monitoring

## Files Created

- `app/services/scheduler.py` - Main scheduler implementation
- `scripts/run_scheduler.py` - Standalone scheduler runner
- `SCHEDULER_GUIDE.md` - Detailed documentation
- `SCHEDULER_SETUP.md` - This file

## Next Steps

1. Install dependencies: `pip install -r requirements.txt`
2. Start the application: `uvicorn app.main:app --reload`
3. Check logs for scheduler startup message
4. Monitor task execution in logs
5. Verify data processing in database
6. Check AI forecasts in frontend

## Support

For issues or questions:
1. Check logs for error messages
2. Verify API endpoints are accessible
3. Ensure database is connected
4. Review SCHEDULER_GUIDE.md for detailed troubleshooting
5. Check APScheduler docs: https://apscheduler.readthedocs.io/
