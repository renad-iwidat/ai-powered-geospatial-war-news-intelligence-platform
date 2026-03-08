# Background Task Scheduler Guide

## Overview

The GeoNews AI platform includes a background task scheduler that automatically runs data processing and AI forecast generation tasks on a schedule. The scheduler uses **APScheduler** with **threading** for parallel execution.

## Scheduled Tasks

### 1. Data Processing (Every 15 minutes)
- **Location Extraction**: Extracts geographic locations from news articles using NER
- **Metrics Extraction**: Extracts numerical metrics (casualties, weapons, etc.) from events
- **Batch Size**: 50 articles for locations, 100 events for metrics
- **Max Instances**: 1 (prevents overlapping executions)

### 2. AI Forecast Generation (Every 10 hours)
- **Intelligence Forecast**: Generates AI-powered predictions using OpenAI GPT
- **Trend Analysis**: Analyzes geopolitical trends
- **Cache Update**: Updates cached forecasts for frontend
- **Max Instances**: 1 (prevents overlapping executions)

## Architecture

```
┌─────────────────────────────────────────┐
│     FastAPI Application (Main)          │
│  ┌───────────────────────────────────┐  │
│  │  Background Scheduler (Threading) │  │
│  │  ┌─────────────────────────────┐  │  │
│  │  │ Worker Thread 1             │  │  │
│  │  │ - Data Processing Job       │  │  │
│  │  └─────────────────────────────┘  │  │
│  │  ┌─────────────────────────────┐  │  │
│  │  │ Worker Thread 2             │  │  │
│  │  │ - AI Forecast Job           │  │  │
│  │  └─────────────────────────────┘  │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

## Usage

### Option 1: Integrated with FastAPI (Recommended)

The scheduler starts automatically when the FastAPI application starts:

```bash
# Start the FastAPI server (scheduler runs in background)
uvicorn app.main:app --reload
```

**Logs will show:**
```
✅ Scheduler started successfully
📅 Jobs scheduled:
   - Data Processing: Every 15 minutes
   - AI Forecast: Every 10 hours
```

### Option 2: Standalone Scheduler Process

Run the scheduler as a separate process (useful for distributed deployments):

```bash
# Make the script executable
chmod +x scripts/run_scheduler.py

# Run the standalone scheduler
python scripts/run_scheduler.py

# Or with custom API URL
API_BASE_URL=http://api.example.com:8000 python scripts/run_scheduler.py
```

### Option 3: Docker Compose (Multiple Services)

Run separate containers for API and scheduler:

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/geonews
    depends_on:
      - db

  scheduler:
    build: .
    command: python scripts/run_scheduler.py
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/geonews
      - API_BASE_URL=http://api:8000
    depends_on:
      - api
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=geonews
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
```

## Parallel Execution

The scheduler uses **2 worker threads** to allow parallel execution:

- **Thread 1**: Handles data processing tasks (every 15 minutes)
- **Thread 2**: Handles AI forecast tasks (every 10 hours)

### Scenario: Overlapping Execution

If both tasks are scheduled to run at the same time:

```
Time: 10:00 AM
├─ Data Processing starts (Thread 1)
├─ AI Forecast starts (Thread 2)  ← Parallel execution
└─ Both run simultaneously
```

The `max_instances=1` setting ensures each job type doesn't overlap with itself, but different job types can run in parallel.

## Monitoring

### View Scheduler Status

Check the application logs for scheduler activity:

```
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
✅ AI forecast generation completed at 2026-03-07T10:15:45
```

### Check Processing Status

Use the API endpoint to check current processing status:

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
# Change data processing interval (default: 15 minutes)
self.scheduler.add_job(
    self._run_data_processing,
    trigger=IntervalTrigger(minutes=15),  # ← Change this
    ...
)

# Change AI forecast interval (default: 10 hours)
self.scheduler.add_job(
    self._run_ai_forecast,
    trigger=IntervalTrigger(hours=10),  # ← Change this
    ...
)
```

### Adjust Batch Sizes

Edit `app/services/scheduler.py`:

```python
# Location extraction batch size (default: 50)
json={"batch_size": 50}  # ← Change this

# Metrics extraction batch size (default: 100)
json={"batch_size": 100}  # ← Change this
```

## Troubleshooting

### Scheduler Not Starting

**Problem**: Scheduler fails to start with FastAPI

**Solution**:
1. Check if APScheduler is installed: `pip install apscheduler`
2. Check logs for error messages
3. Ensure API endpoints are accessible
4. Try running standalone scheduler to isolate the issue

### Tasks Not Running

**Problem**: Scheduled tasks are not executing

**Solution**:
1. Check if scheduler is running: Look for "✅ Scheduler started successfully" in logs
2. Verify API endpoints are accessible: `curl http://localhost:8000/health`
3. Check database connectivity
4. Review logs for specific error messages

### High CPU Usage

**Problem**: Scheduler consuming too much CPU

**Solution**:
1. Increase interval times (e.g., 30 minutes instead of 15)
2. Reduce batch sizes
3. Check if tasks are completing successfully
4. Monitor database performance

### Memory Leaks

**Problem**: Memory usage increasing over time

**Solution**:
1. Ensure tasks complete successfully
2. Check for unclosed connections in task code
3. Monitor database connection pool
4. Consider running scheduler in separate process

## Performance Tips

1. **Stagger Schedules**: Avoid running all tasks at the same time
   ```python
   # Run data processing at :00, :15, :30, :45
   # Run AI forecast at 2 AM, 12 PM, 10 PM
   ```

2. **Optimize Batch Sizes**: Balance between throughput and resource usage
   ```python
   # Smaller batches = more frequent, less resource intensive
   # Larger batches = less frequent, more resource intensive
   ```

3. **Use Separate Process**: For production, run scheduler in separate container
   ```bash
   # Prevents scheduler from blocking API requests
   ```

4. **Monitor Resources**: Track CPU, memory, and database connections
   ```bash
   # Use tools like htop, docker stats, or cloud monitoring
   ```

## API Endpoints Used by Scheduler

The scheduler calls these internal API endpoints:

1. **Location Extraction**
   ```
   POST /api/v1/data-processing/extract-locations
   Body: {"batch_size": 50}
   ```

2. **Metrics Extraction**
   ```
   POST /api/v1/data-processing/extract-metrics
   Body: {"batch_size": 100}
   ```

3. **Intelligence Forecast**
   ```
   GET /api/v1/predictions/intelligence-forecast?days=7&force_refresh=true
   ```

4. **Trend Analysis**
   ```
   GET /api/v1/predictions/trend-analysis
   ```

## Deployment Checklist

- [ ] APScheduler installed: `pip install apscheduler`
- [ ] Database connectivity verified
- [ ] API endpoints accessible
- [ ] Logging configured
- [ ] Environment variables set (API_BASE_URL, DATABASE_URL, OPENAI_API_KEY)
- [ ] Scheduler running (check logs for "✅ Scheduler started successfully")
- [ ] Tasks executing on schedule (check logs for task execution)
- [ ] Error handling working (check logs for error messages)
- [ ] Resource usage monitored (CPU, memory, database connections)

## Support

For issues or questions:
1. Check the logs for error messages
2. Verify API endpoints are accessible
3. Ensure database is connected
4. Review this guide for troubleshooting steps
5. Check APScheduler documentation: https://apscheduler.readthedocs.io/
