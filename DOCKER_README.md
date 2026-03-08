# GeoNews AI - Docker Setup

## 🎯 Architecture

```
docker-compose up -d
    ↓
┌─────────────────────────────────────┐
│   Backend Container (port 7235)     │
├─────────────────────────────────────┤
│  • FastAPI Server (API)             │
│  • Background Scheduler             │
│    - Data Processing (15 min)       │
│    - AI Forecast (10 hours)         │
└─────────────────────────────────────┘
         ↑                    ↓
         │              Database (Render)
         │
┌─────────────────────────────────────┐
│   Frontend Container (port 3001)    │
├─────────────────────────────────────┤
│  • Next.js Application              │
│  • Calls Backend API                │
└─────────────────────────────────────┘
```

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Copy example env
cp .env.example .env

# Edit .env with your values:
# - DATABASE_URL (from Render)
# - OPENAI_API_KEY
```

### 2. Start Services
```bash
# Build and start all services
docker-compose up -d

# Check status
docker-compose ps
```

### 3. Access Application
- **Frontend**: http://localhost:3001
- **Backend API**: http://localhost:7235
- **API Docs**: http://localhost:7235/docs

## 📊 What's Running

### Backend Container
- **API Server**: FastAPI on port 7235
- **Scheduler**: Integrated, runs automatically
  - Data Processing: Every 15 minutes
  - AI Forecast: Every 10 hours

### Frontend Container
- **Web App**: Next.js on port 3001
- **Calls**: Backend API at http://backend:7235

### Database
- **Location**: Render (external)
- **Connection**: Via DATABASE_URL env variable

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Database (from Render)
DATABASE_URL=postgresql://...

# API Keys
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o

# Ports
BACKEND_PORT=7235
FRONTEND_PORT=3001

# CORS
CORS_ORIGINS=http://localhost:3001,http://frontend:3001

# Scheduler
API_BASE_URL=http://backend:7235
```

## 📝 Common Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Follow scheduler jobs
docker-compose logs -f backend | grep "🔄\|✅\|❌"
```

### Stop Services
```bash
docker-compose down
```

### Restart Services
```bash
docker-compose restart
```

### Rebuild Images
```bash
docker-compose build --no-cache
docker-compose up -d
```

## 🧪 Testing

### Test Backend Health
```bash
curl http://localhost:7235/health
```

### Test Frontend
```bash
curl http://localhost:3001
```

### Test API Endpoint
```bash
curl http://localhost:7235/api/v1/analytics/statistics
```

## 📋 Scheduler Jobs

### Data Processing (Every 15 minutes)
- Extracts locations from news articles
- Extracts metrics from events

### AI Forecast (Every 10 hours)
- Generates intelligence forecast
- Generates trend analysis

**View job execution in logs:**
```bash
docker-compose logs -f backend
```

## 🛠️ Troubleshooting

### Services won't start
```bash
# Check logs
docker-compose logs

# Rebuild
docker-compose build --no-cache
docker-compose up -d
```

### Database connection fails
- Verify DATABASE_URL is correct
- Check Render database is accessible
- Ensure firewall allows connection

### Frontend can't reach backend
- Check backend is running: `docker-compose ps`
- Check logs: `docker-compose logs backend`
- Verify NEXT_PUBLIC_API_URL is set

### Port conflicts
```bash
# Change ports in .env
BACKEND_PORT=7236
FRONTEND_PORT=3002

# Restart
docker-compose down
docker-compose up -d
```

## 📚 Documentation

- **DOCKER_SETUP.md** - Comprehensive setup guide
- **DOCKER_QUICKSTART.md** - Quick start guide
- **SCHEDULER_DOCKER_GUIDE.md** - Scheduler configuration
- **DOCKER_VERIFICATION.md** - Verification checklist

## ✅ Checklist

Before running `docker-compose up -d`:

- [ ] .env file created and configured
- [ ] DATABASE_URL is correct
- [ ] OPENAI_API_KEY is set
- [ ] Ports 7235 and 3001 are available
- [ ] Docker and Docker Compose installed

## 🎉 Ready to Go!

```bash
docker-compose up -d
```

Everything will start automatically:
- Backend API + Scheduler
- Frontend
- All connections configured

Monitor with:
```bash
docker-compose logs -f
```
