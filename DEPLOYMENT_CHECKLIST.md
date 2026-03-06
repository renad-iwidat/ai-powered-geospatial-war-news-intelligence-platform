# 🚀 GeoNews AI - Deployment Checklist

## ✅ Pre-Deployment Tests (All Passed!)

### Backend Tests
- [x] Database Connection - 974 news articles
- [x] API Health Check - Healthy
- [x] News Endpoint - Working (974 articles)
- [x] Analytics Endpoint - Working (50 timeline items)
- [x] AI Forecast Endpoint - Working (cached)
- [x] Processing Status - 13.5% completion

### Data Processing Tests
- [x] Location Processing - ✅ Processed 10 news → 26 events
- [x] Metrics Extraction - ✅ Processed 20 events
- [x] AI Forecast Generation - ✅ Generated with GPT-4o
- [x] Forecast Caching - ✅ 6 forecasts cached

### Frontend Tests
- [x] Frontend Running - http://localhost:3000
- [x] English Version - /en
- [x] Arabic Version - /ar
- [x] API Integration - Working

---

## 📊 Current System Status

### Database
- **Total News**: 974 articles
- **With Events**: 231 (23.7%)
- **Without Events**: 743 (need processing)
- **Total Events**: 448
- **With Metrics**: 15 (3.3%)
- **Without Metrics**: 433 (need processing)
- **AI Forecasts**: 6 cached (all valid)

### AI Configuration
- **Model**: GPT-4o (upgraded from gpt-4o-mini)
- **Temperature**: 0.2 (for consistency)
- **Max Tokens**: 3000
- **Prompts**: Neutral and objective
- **Caching**: Twice daily (1 PM & 9 PM Palestine time)

### Processing Pipeline
```
Every 15 minutes:
├─ Location Processing: 20 news/batch
│  ├─ NER extraction (CAMeL Tools)
│  ├─ Geocoding (Nominatim)
│  └─ Store locations & events
│
└─ Metrics Extraction: 20 events/batch
   ├─ Extract numbers (regex patterns)
   └─ Store metrics

Twice daily (1 PM & 9 PM):
└─ AI Forecast Generation
   ├─ Intelligence forecast (7 days)
   ├─ Trend analysis
   └─ Cache for 8 hours
```

---

## 🔧 Deployment Configuration

### Environment Variables (.env)
```bash
# Database
DATABASE_URL=postgresql://...

# OpenAI (Required for AI forecasts)
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o

# API
API_V1_PREFIX=/api/v1
PROJECT_NAME=GeoNews AI
PROJECT_VERSION=1.0.0

# CORS
CORS_ORIGINS=["*"]

# Geocoding
NOMINATIM_URL=https://nominatim.openstreetmap.org/search
GEOCODING_USER_AGENT=GeoNewsAI/1.0 (contact: lmaaljohare@gmail.com)
GEOCODING_SLEEP_SECONDS=1.0
```

### Frontend Environment (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 📦 Render Deployment

### 1. Backend (Web Service)
```yaml
name: geonews-ai-backend
type: web
env: python
buildCommand: pip install -r requirements.txt
startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
envVars:
  - key: DATABASE_URL
    fromDatabase:
      name: geonews-db
      property: connectionString
  - key: OPENAI_API_KEY
    sync: false
  - key: OPENAI_MODEL
    value: gpt-4o
```

### 2. Frontend (Static Site)
```yaml
name: geonews-ai-frontend
type: web
env: node
buildCommand: cd frontend && npm install && npm run build
startCommand: cd frontend && npm start
envVars:
  - key: NEXT_PUBLIC_API_URL
    value: https://geonews-ai-backend.onrender.com
```

### 3. Data Processing (Cron Job - Every 15 minutes)
```yaml
name: data-processor
type: cron
schedule: "*/15 * * * *"
env: python
buildCommand: pip install -r requirements.txt
startCommand: python scripts/process_batch.py
envVars:
  - key: DATABASE_URL
    fromDatabase:
      name: geonews-db
      property: connectionString
```

### 4. AI Forecast Generator (Cron Job - 1 PM Palestine = 11 AM UTC)
```yaml
name: ai-forecast-1pm
type: cron
schedule: "0 11 * * *"
env: python
buildCommand: pip install -r requirements.txt
startCommand: python scripts/generate_ai_forecasts.py
envVars:
  - key: DATABASE_URL
    fromDatabase:
      name: geonews-db
      property: connectionString
  - key: OPENAI_API_KEY
    sync: false
  - key: OPENAI_MODEL
    value: gpt-4o
```

### 5. AI Forecast Generator (Cron Job - 9 PM Palestine = 7 PM UTC)
```yaml
name: ai-forecast-9pm
type: cron
schedule: "0 19 * * *"
env: python
buildCommand: pip install -r requirements.txt
startCommand: python scripts/generate_ai_forecasts.py
envVars:
  - key: DATABASE_URL
    fromDatabase:
      name: geonews-db
      property: connectionString
  - key: OPENAI_API_KEY
    sync: false
  - key: OPENAI_MODEL
    value: gpt-4o
```

---

## ⚙️ Post-Deployment Steps

### 1. Verify Backend
```bash
curl https://your-backend.onrender.com/health
# Expected: {"status":"healthy","database":"connected","version":"1.0.0"}
```

### 2. Verify Frontend
```bash
curl https://your-frontend.onrender.com
# Expected: 200 OK
```

### 3. Test API Endpoints
```bash
# News
curl https://your-backend.onrender.com/api/v1/news-articles?limit=5

# Analytics
curl https://your-backend.onrender.com/api/v1/analytics/timeline?days=7

# AI Forecast (cached)
curl https://your-backend.onrender.com/api/v1/predictions/ai-intelligence-forecast
```

### 4. Monitor Cron Jobs
- Check Render dashboard for cron job execution logs
- Verify data processing is running every 15 minutes
- Verify AI forecasts are generated at 1 PM and 9 PM

### 5. Check Database
```sql
-- Check processing progress
SELECT 
  COUNT(*) as total_news,
  COUNT(DISTINCT ne.raw_news_id) as with_events,
  (COUNT(DISTINCT ne.raw_news_id)::float / COUNT(*)::float * 100) as completion_pct
FROM raw_news rn
LEFT JOIN news_events ne ON rn.id = ne.raw_news_id;

-- Check AI forecasts
SELECT 
  forecast_type,
  generated_at,
  valid_until,
  forecast_data->>'trend' as trend,
  forecast_data->>'confidence_overall' as confidence
FROM ai_forecasts
WHERE valid_until > NOW()
ORDER BY generated_at DESC;
```

---

## 🔍 Monitoring & Maintenance

### Daily Checks
- [ ] Backend health status
- [ ] Frontend accessibility
- [ ] Cron jobs execution (check logs)
- [ ] Database connection
- [ ] AI forecast cache validity

### Weekly Checks
- [ ] Processing completion percentage
- [ ] API response times
- [ ] Error logs review
- [ ] Database size and performance

### Monthly Checks
- [ ] OpenAI API usage and costs
- [ ] Geocoding API rate limits
- [ ] Database cleanup (old forecasts)
- [ ] Performance optimization

---

## 📈 Expected Costs (Monthly)

### Render
- **Web Services**: $7/month × 2 = $14/month
- **Cron Jobs**: Free tier (3 jobs)
- **Database**: $7/month (Starter)
- **Total Render**: ~$21/month

### OpenAI API
- **AI Forecasts**: 2 calls/day × 30 days = 60 calls/month
- **Cost per call**: ~$0.10
- **Total OpenAI**: ~$6/month

### **Grand Total**: ~$27/month

---

## 🎯 Success Criteria

- [x] All 6 tests passing
- [x] Backend API responding
- [x] Frontend loading
- [x] Database connected
- [x] AI forecasts generating
- [x] Processing pipeline working
- [x] Caching system functional

---

## 🚨 Troubleshooting

### Backend not starting
1. Check DATABASE_URL is set
2. Check Python version (3.11+)
3. Check requirements.txt installed
4. Check logs: `render logs <service-name>`

### Frontend not loading
1. Check NEXT_PUBLIC_API_URL is set
2. Check backend is running
3. Check CORS settings
4. Check build logs

### Cron jobs not running
1. Check schedule syntax (cron format)
2. Check environment variables
3. Check script paths
4. Check logs in Render dashboard

### AI forecasts failing
1. Check OPENAI_API_KEY is set
2. Check API quota/billing
3. Check database connection
4. Run manually: `python scripts/generate_ai_forecasts.py`

---

## ✅ Final Checklist

Before deploying:
- [x] All tests passed (6/6)
- [x] Environment variables documented
- [x] Cron schedules configured
- [x] Database migrations ready
- [x] Frontend build successful
- [x] API endpoints tested
- [x] AI forecasts working
- [x] Processing pipeline verified

**Status**: ✅ READY FOR DEPLOYMENT

---

## 📞 Support

For issues or questions:
- Check logs in Render dashboard
- Run test script: `python scripts/test_full_pipeline.py`
- Review this checklist
- Check error messages in browser console (frontend)
- Check API response codes (backend)

---

**Last Updated**: 2026-03-06
**Version**: 1.0.0
**Status**: Production Ready ✅
