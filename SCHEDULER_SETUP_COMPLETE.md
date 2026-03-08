# ✅ Scheduler Setup Complete

## 📦 Files Created

```
✅ Dockerfile.scheduler              - Scheduler image
✅ docker-compose.scheduler.yml      - Scheduler + Backend compose
✅ SCHEDULER_DEPLOYMENT.md           - Detailed guide
✅ SCHEDULER_QUICK_START.md          - Quick reference
```

## 🎯 What It Does

الـ Scheduler container يشتغل:

### Data Processing (Every 15 minutes)
```
POST /api/v1/data-processing/extract-locations
POST /api/v1/data-processing/extract-metrics
```
- استخراج الـ locations من الـ news articles
- استخراج الـ metrics من الـ events

### AI Analysis (Every 10 hours)
```
GET /api/v1/predictions/intelligence-forecast
GET /api/v1/predictions/trend-analysis
```
- تحليل الـ trends
- توليد الـ forecasts

## 🚀 Quick Start

```bash
# Start scheduler + backend
docker-compose -f docker-compose.scheduler.yml up -d

# View logs
docker-compose -f docker-compose.scheduler.yml logs -f scheduler

# Stop
docker-compose -f docker-compose.scheduler.yml down
```

## 🔧 Configuration

الـ .env يحتوي على:
```
DATABASE_URL=postgresql://...          # Render database ✅
OPENAI_API_KEY=sk-...                  # OpenAI key ✅
API_BASE_URL=http://backend:7235       # Backend URL ✅
```

## 📊 Architecture

```
docker-compose.scheduler.yml
├─ Scheduler Container
│  ├─ Data Processing (15 min)
│  └─ AI Analysis (10 hours)
└─ Backend Container (required)
   └─ API Server (port 7235)
```

## 🧪 Testing

```bash
# Check scheduler is running
docker-compose -f docker-compose.scheduler.yml ps

# View job execution
docker-compose -f docker-compose.scheduler.yml logs -f scheduler

# Expected output:
# 🔄 Starting data processing at 2024-03-07T10:30:00
# ✓ Locations extracted: 50 articles processed
# ✓ Metrics extracted: 100 events processed
# ✅ Data processing completed
```

## 📝 Environment Variables

```bash
# Required
DATABASE_URL=postgresql://war_news_intelligence_user:...@dpg-d6k9ce4r85hc73c4qmr0-a.oregon-postgres.render.com/war_news_intelligence
OPENAI_API_KEY=sk-proj-...
API_BASE_URL=http://backend:7235

# Optional
OPENAI_MODEL=gpt-4o
NEWS_VIEW_NAME=vw_news_ar_feed
```

## 🎯 Usage Scenarios

### Scenario 1: Full Application
```bash
# Terminal 1: Run full app (API + Frontend)
docker-compose up -d

# Terminal 2: Run scheduler separately
docker-compose -f docker-compose.scheduler.yml up -d scheduler
```

### Scenario 2: Scheduler Only
```bash
# Run scheduler with backend (no frontend)
docker-compose -f docker-compose.scheduler.yml up -d
```

### Scenario 3: Local Development
```bash
# Set environment variables
export DATABASE_URL="postgresql://..."
export OPENAI_API_KEY="sk-..."
export API_BASE_URL="http://localhost:7235"

# Run scheduler
python scripts/run_scheduler.py
```

## 📊 Image Size

- Scheduler Image: ~2.5-3.5 GB
- Build Time: ~10-15 minutes

## 🛠️ Troubleshooting

### Scheduler not connecting to backend
```bash
# Check backend is running
docker-compose -f docker-compose.scheduler.yml ps backend

# Test connectivity
docker-compose -f docker-compose.scheduler.yml exec scheduler curl http://backend:7235/health
```

### Database connection fails
- Verify DATABASE_URL is correct
- Check Render database is accessible

### Jobs not executing
- Check API_BASE_URL is correct
- Check backend logs: `docker-compose -f docker-compose.scheduler.yml logs backend`

## 📚 Documentation

- **SCHEDULER_DEPLOYMENT.md** - Detailed deployment guide
- **SCHEDULER_QUICK_START.md** - Quick reference
- **scripts/run_scheduler.py** - Scheduler entry point
- **app/services/scheduler.py** - Scheduler implementation

## ✅ Ready to Deploy!

```bash
docker-compose -f docker-compose.scheduler.yml up -d
```

الـ Scheduler بتشتغل تلقائياً!

## 🎉 Summary

- ✅ Dockerfile.scheduler created
- ✅ docker-compose.scheduler.yml created
- ✅ Configuration complete
- ✅ Ready for deployment

الـ Scheduler جاهز للـ production!
