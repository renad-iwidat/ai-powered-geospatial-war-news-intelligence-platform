# Scheduler Quick Start

## 🚀 Run Scheduler with Backend

```bash
# Start scheduler + backend
docker-compose -f docker-compose.scheduler.yml up -d

# View logs
docker-compose -f docker-compose.scheduler.yml logs -f scheduler

# Stop
docker-compose -f docker-compose.scheduler.yml down
```

## 📊 What's Running

```
Scheduler Container
├─ Data Processing (every 15 min)
│  ├─ Extract locations from news
│  └─ Extract metrics from events
└─ AI Analysis (every 10 hours)
   ├─ Generate intelligence forecast
   └─ Generate trend analysis

Backend Container (required)
└─ API Server (port 7235)
```

## 🔧 Configuration

```bash
# .env file
DATABASE_URL=postgresql://...          # Render database
OPENAI_API_KEY=sk-...                  # OpenAI key
API_BASE_URL=http://backend:7235       # Backend URL
```

## 📝 Common Commands

```bash
# View scheduler logs
docker-compose -f docker-compose.scheduler.yml logs -f scheduler

# Check status
docker-compose -f docker-compose.scheduler.yml ps

# Restart scheduler
docker-compose -f docker-compose.scheduler.yml restart scheduler

# View job execution
docker-compose -f docker-compose.scheduler.yml logs scheduler | grep "🔄\|✅"
```

## 🧪 Testing

```bash
# Check backend health
curl http://localhost:7235/health

# Check scheduler logs for job execution
docker-compose -f docker-compose.scheduler.yml logs -f scheduler
```

## 📚 Files

- `Dockerfile.scheduler` - Scheduler image
- `docker-compose.scheduler.yml` - Scheduler + Backend compose
- `scripts/run_scheduler.py` - Scheduler entry point
- `app/services/scheduler.py` - Scheduler implementation

## ✅ Ready!

```bash
docker-compose -f docker-compose.scheduler.yml up -d
```

That's it! Scheduler is running.
