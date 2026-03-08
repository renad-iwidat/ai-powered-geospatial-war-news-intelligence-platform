# Docker Complete Setup - All-in-One

## 🎯 What You Get

When you run `docker-compose up -d`, you get:

```
✅ Backend Container (port 7235)
   ├─ FastAPI Server (API)
   └─ Background Scheduler
      ├─ Data Processing (every 15 min)
      └─ AI Forecast (every 10 hours)

✅ Frontend Container (port 3001)
   └─ Next.js Application

✅ Database (Render - external)
   └─ PostgreSQL connection via DATABASE_URL
```

## 🚀 One Command to Start Everything

```bash
# 1. Setup environment (one time)
cp .env.example .env
# Edit .env with DATABASE_URL and OPENAI_API_KEY

# 2. Start everything
docker-compose up -d

# 3. Done! Everything is running
```

## 📊 What's Included

### Backend Container
- **API Server**: FastAPI on port 7235
- **Scheduler**: Runs automatically in background
  - Extracts locations from news (every 15 min)
  - Extracts metrics from events (every 15 min)
  - Generates AI forecast (every 10 hours)
  - Generates trend analysis (every 10 hours)

### Frontend Container
- **Web App**: Next.js on port 3001
- **Calls**: Backend API at http://backend:7235

### Database
- **Hosted**: Render (external)
- **Connection**: Via DATABASE_URL environment variable

## 🔗 How They Connect

```
User Browser
    ↓
http://localhost:3001 (Frontend)
    ↓
http://backend:7235 (Backend API)
    ↓
Render Database
```

## 📝 Environment Variables

```bash
# .env file
DATABASE_URL=postgresql://...          # From Render
OPENAI_API_KEY=sk-...                  # Your OpenAI key
OPENAI_MODEL=gpt-4o                    # Model to use
NEWS_VIEW_NAME=vw_news_ar_feed         # Database view
BACKEND_PORT=7235                      # External backend port
FRONTEND_PORT=3001                     # External frontend port
CORS_ORIGINS=http://localhost:3001     # CORS allowed origins
API_BASE_URL=http://backend:7235       # Scheduler API URL
```

## 🧪 Testing

### Check Everything is Running
```bash
# View all containers
docker-compose ps

# Should show:
# geonews-backend    running
# geonews-frontend   running
```

### Test Backend
```bash
# Health check
curl http://localhost:7235/health

# API Docs
curl http://localhost:7235/docs

# Sample API call
curl http://localhost:7235/api/v1/analytics/statistics
```

### Test Frontend
```bash
# Open in browser
http://localhost:3001
```

### View Scheduler Logs
```bash
# See scheduler jobs running
docker-compose logs -f backend | grep "🔄\|✅\|❌"

# Example output:
# 🔄 Starting data processing at 2024-03-07T10:30:00
# ✓ Locations extracted: 50 articles processed
# ✓ Metrics extracted: 100 events processed
# ✅ Data processing completed at 2024-03-07T10:35:00
```

## 📋 Common Tasks

### View All Logs
```bash
docker-compose logs -f
```

### View Backend Logs Only
```bash
docker-compose logs -f backend
```

### View Frontend Logs Only
```bash
docker-compose logs -f frontend
```

### Stop Everything
```bash
docker-compose down
```

### Restart Everything
```bash
docker-compose restart
```

### Rebuild and Start
```bash
docker-compose build --no-cache
docker-compose up -d
```

### Access Backend Shell
```bash
docker-compose exec backend bash
```

### Access Frontend Shell
```bash
docker-compose exec frontend sh
```

## 🛠️ Troubleshooting

### Services won't start
```bash
# Check what's wrong
docker-compose logs

# Rebuild everything
docker-compose build --no-cache
docker-compose up -d
```

### Database connection error
- Verify DATABASE_URL is correct
- Check Render database is accessible
- Ensure firewall allows connection

### Frontend can't reach backend
```bash
# Check backend is running
docker-compose ps backend

# Check backend logs
docker-compose logs backend

# Test connectivity
docker-compose exec frontend curl http://backend:7235/health
```

### Port already in use
```bash
# Change ports in .env
BACKEND_PORT=7236
FRONTEND_PORT=3002

# Restart
docker-compose down
docker-compose up -d
```

### Scheduler not running
```bash
# Check backend logs
docker-compose logs backend

# Look for "Scheduler started successfully"
docker-compose logs backend | grep "Scheduler"
```

## 📊 Scheduler Details

### Jobs Running
1. **Data Processing** (every 15 minutes)
   - POST /api/v1/data-processing/extract-locations
   - POST /api/v1/data-processing/extract-metrics

2. **AI Forecast** (every 10 hours)
   - GET /api/v1/predictions/intelligence-forecast
   - GET /api/v1/predictions/trend-analysis

### Monitor Jobs
```bash
# Follow scheduler execution
docker-compose logs -f backend

# Filter for job messages
docker-compose logs backend | grep "🔄\|✅\|❌\|ERROR"
```

## 🎯 Architecture

```
┌─────────────────────────────────────────────────────┐
│              Docker Compose Network                 │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │  Backend Container (port 7235)               │  │
│  ├──────────────────────────────────────────────┤  │
│  │  • FastAPI Server                            │  │
│  │  • Background Scheduler                      │  │
│  │    - Data Processing (15 min)                │  │
│  │    - AI Forecast (10 hours)                  │  │
│  └──────────────────────────────────────────────┘  │
│                      ↑                              │
│                      │ (API calls)                  │
│                      │                              │
│  ┌──────────────────────────────────────────────┐  │
│  │  Frontend Container (port 3001)              │  │
│  ├──────────────────────────────────────────────┤  │
│  │  • Next.js Application                       │  │
│  │  • Calls Backend API                         │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
└─────────────────────────────────────────────────────┘
                      ↓
            ┌──────────────────┐
            │  Render Database │
            │  (PostgreSQL)    │
            └──────────────────┘
```

## ✅ Checklist

Before running `docker-compose up -d`:

- [ ] Docker installed
- [ ] Docker Compose installed
- [ ] .env file created
- [ ] DATABASE_URL configured
- [ ] OPENAI_API_KEY configured
- [ ] Ports 7235 and 3001 available

## 🎉 Ready to Go!

```bash
# One command to start everything
docker-compose up -d

# Monitor
docker-compose logs -f

# Access
# Frontend: http://localhost:3001
# Backend: http://localhost:7235
# API Docs: http://localhost:7235/docs
```

## 📚 Documentation

- **DOCKER_README.md** - Quick overview
- **DOCKER_SETUP.md** - Detailed setup guide
- **DOCKER_QUICKSTART.md** - Quick start
- **SCHEDULER_DOCKER_GUIDE.md** - Scheduler details
- **DOCKER_VERIFICATION.md** - Verification checklist

## 🚀 That's It!

Everything is configured and ready to run. Just:

1. Setup .env
2. Run `docker-compose up -d`
3. Access http://localhost:3001

All services (API, Scheduler, Frontend) will start automatically!
