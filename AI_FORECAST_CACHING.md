# AI Forecast Caching System

## 📋 Overview

نظام تخزين مؤقت (caching) للتحليلات الذكية لتقليل تكاليف OpenAI API بنسبة 95%+

## 🎯 Problem

- كل user يطلب AI analysis = API call جديد
- 100 users/day × $0.05/call = **$5/day = $150/month** 💸
- مكلف جداً للتحليلات المتكررة

## ✅ Solution

- توليد التحليلات **مرتين باليوم فقط** (1 PM و 9 PM بتوقيت فلسطين)
- تخزين النتائج في الداتابيس
- كل الـ users يقروا من الـ cache
- **2 calls/day × $0.05 = $0.10/day = $3/month** 💰

**التوفير: 98%** 🎉

---

## 🗄️ Database Schema

### Table: `ai_forecasts`

```sql
CREATE TABLE ai_forecasts (
    id SERIAL PRIMARY KEY,
    forecast_type VARCHAR(50) NOT NULL,  -- 'intelligence_forecast', 'trend_analysis'
    forecast_data JSONB NOT NULL,        -- Complete AI response
    days_ahead INTEGER,                  -- Forecast period
    generated_at TIMESTAMP NOT NULL,
    valid_until TIMESTAMP NOT NULL,      -- Expires after 8 hours
    model_info JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🚀 Setup Instructions

### Step 1: Run Migration

```bash
python scripts/run_migration.py
```

هاد بينشئ جدول `ai_forecasts` في الداتابيس.

### Step 2: Test Forecast Generation (Manual)

```bash
python scripts/generate_ai_forecasts.py
```

هاد بيولد التحليلات ويخزنها. استخدمه للتجربة.

### Step 3: Configure Scheduled Jobs on Render

في `render.yaml` أو من الـ dashboard، أضف cron jobs:

```yaml
services:
  # Existing web service...
  
  # AI Forecast Generator - 1 PM Palestine Time (11 AM UTC)
  - type: cron
    name: ai-forecast-1pm
    env: python
    schedule: "0 11 * * *"
    buildCommand: "pip install -r requirements.txt"
    startCommand: "python scripts/generate_ai_forecasts.py"
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: your-database-name
          property: connectionString
      - key: OPENAI_API_KEY
        sync: false
  
  # AI Forecast Generator - 9 PM Palestine Time (7 PM UTC)
  - type: cron
    name: ai-forecast-9pm
    env: python
    schedule: "0 19 * * *"
    buildCommand: "pip install -r requirements.txt"
    startCommand: "python scripts/generate_ai_forecasts.py"
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: your-database-name
          property: connectionString
      - key: OPENAI_API_KEY
        sync: false
```

**ملاحظة**: Palestine Time = UTC+2 (أو UTC+3 في الصيف)
- 1 PM Palestine = 11 AM UTC (winter) / 10 AM UTC (summer)
- 9 PM Palestine = 7 PM UTC (winter) / 6 PM UTC (summer)

---

## 📡 API Changes

### Before (Direct AI Call)

```
GET /api/v1/predictions/ai-intelligence-forecast
→ Calls OpenAI API every time
→ Expensive 💸
```

### After (Cached)

```
GET /api/v1/predictions/ai-intelligence-forecast
→ Returns cached forecast (generated at 1 PM or 9 PM)
→ Fast & cheap ⚡💰

GET /api/v1/predictions/ai-intelligence-forecast?force_refresh=true
→ Bypass cache (admin only)
→ Generates new forecast
```

---

## 🔄 How It Works

### 1. Scheduled Generation (Twice Daily)

```
1 PM Palestine Time:
  ├─ Fetch last 60 days of data
  ├─ Fetch last 20 news articles
  ├─ Call OpenAI API
  ├─ Store result in ai_forecasts table
  └─ Set valid_until = NOW() + 8 hours

9 PM Palestine Time:
  └─ Same process
```

### 2. API Request Flow

```
User requests forecast
    ↓
Check ai_forecasts table
    ↓
Valid cache exists? ─── YES ──→ Return cached data ✅
    ↓
   NO
    ↓
force_refresh=true? ─── YES ──→ Generate new forecast
    ↓
   NO
    ↓
Return error: "No cached forecast available"
```

### 3. Automatic Cleanup

```
Every run:
  └─ Delete forecasts older than 7 days
```

---

## 📊 Monitoring

### Check Latest Forecast

```sql
SELECT 
    forecast_type,
    generated_at,
    valid_until,
    forecast_data->>'trend' as trend,
    forecast_data->>'confidence_overall' as confidence
FROM ai_forecasts
ORDER BY generated_at DESC
LIMIT 5;
```

### Check Cache Hit Rate

```sql
-- Add logging to track cache hits vs misses
-- Monitor in application logs
```

---

## 🧪 Testing

### 1. Test Migration

```bash
python scripts/run_migration.py
```

### 2. Test Forecast Generation

```bash
python scripts/generate_ai_forecasts.py
```

Expected output:
```
🤖 Generating AI Intelligence Forecast (7 days)...
   📊 Historical data: 60 days
   📰 Recent articles: 20 articles
   ✅ Forecast generated and stored (ID: 1)
   📈 Trend: escalating
   🎯 Confidence: 75%
   ⚠️  Risk Level: high

📊 Generating AI Trend Analysis...
   ✅ Trend analysis stored (ID: 2)
```

### 3. Test API Endpoint

```bash
curl http://localhost:8000/api/v1/predictions/ai-intelligence-forecast
```

Should return cached forecast with `cache_info` metadata.

---

## 💡 Best Practices

1. **Schedule Times**: Choose times when data is fresh (after news processing)
2. **Valid Duration**: 8 hours ensures fresh forecasts (2 runs/day)
3. **Cleanup**: Keep 7 days of history for debugging
4. **Monitoring**: Log cache hits/misses to track effectiveness
5. **Fallback**: If cache expires, show last available forecast with warning

---

## 🔧 Troubleshooting

### No cached forecast available

**Problem**: API returns error "No cached forecast available"

**Solution**:
1. Check if cron jobs are running: `render logs <service-name>`
2. Manually run: `python scripts/generate_ai_forecasts.py`
3. Check database: `SELECT * FROM ai_forecasts ORDER BY generated_at DESC LIMIT 1;`

### Forecast expired

**Problem**: `valid_until` is in the past

**Solution**: Cron job didn't run. Check Render logs and re-run manually.

### OpenAI API error

**Problem**: Forecast generation fails

**Solution**:
1. Check `OPENAI_API_KEY` is set
2. Check API quota/billing
3. Check logs: `python scripts/generate_ai_forecasts.py`

---

## 📈 Cost Comparison

### Without Caching
- 100 users/day × 2 endpoints = 200 API calls/day
- 200 × $0.05 = **$10/day**
- **$300/month** 💸

### With Caching
- 2 scheduled runs/day × 2 endpoints = 4 API calls/day
- 4 × $0.05 = **$0.20/day**
- **$6/month** 💰

**Savings: $294/month (98%)** 🎉

---

## 🎯 Next Steps

1. ✅ Run migration
2. ✅ Test forecast generation locally
3. ✅ Deploy to Render
4. ✅ Configure cron jobs
5. ✅ Monitor logs
6. ✅ Update frontend to show cache timestamp

---

## 📝 Notes

- Cache is **per forecast type**, not per user
- All users see the **same forecast** (generated at scheduled time)
- Use `force_refresh=true` only for testing/debugging
- Frontend should display "Last updated: [timestamp]" to users
