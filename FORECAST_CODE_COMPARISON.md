# Forecast Generation Code Comparison

## ✅ التأكيد: الكود متطابق تماماً

### 1. SQL Query - Identical ✅

**Scheduler (`app/services/scheduler.py`):**
```sql
SELECT
    DATE(COALESCE(rn.published_at, rn.fetched_at)) as date,
    COUNT(DISTINCT ne.id) as count
FROM raw_news rn
LEFT JOIN news_events ne ON rn.id = ne.raw_news_id
WHERE COALESCE(rn.published_at, rn.fetched_at) >= CURRENT_DATE - INTERVAL '60 days'
GROUP BY DATE(COALESCE(rn.published_at, rn.fetched_at))
ORDER BY date ASC
```

**Manual Script (`scripts/generate_forecast_simple.py`):**
```sql
SELECT
    DATE(COALESCE(rn.published_at, rn.fetched_at)) as date,
    COUNT(DISTINCT ne.id) as count
FROM raw_news rn
LEFT JOIN news_events ne ON rn.id = ne.raw_news_id
WHERE COALESCE(rn.published_at, rn.fetched_at) >= CURRENT_DATE - INTERVAL '60 days'
GROUP BY DATE(COALESCE(rn.published_at, rn.fetched_at))
ORDER BY date ASC
```

**Result:** ✅ **IDENTICAL**

---

### 2. Data Processing - Identical ✅

**Scheduler:**
```python
historical_data = [
    {'date': row['date'].isoformat(), 'count': row['count']}
    for row in rows
]

recent_articles = [
    {
        'title': row['title'],
        'content': row['content'][:500] if row['content'] else '',
        'published_at': row['published_at'].isoformat() if row['published_at'] else 'Unknown',
        'source': row['source_name']
    }
    for row in article_rows
]
```

**Manual Script:**
```python
historical_data = [
    {'date': row['date'].isoformat(), 'count': row['count']}
    for row in rows
]

recent_articles = [
    {
        'title': row['title'],
        'content': row['content'][:500] if row['content'] else '',
        'published_at': row['published_at'].isoformat() if row['published_at'] else 'Unknown',
        'source': row['source_name']
    }
    for row in article_rows
]
```

**Result:** ✅ **IDENTICAL**

---

### 3. AI Analysis Call - Identical ✅

**Scheduler:**
```python
analyzer = IntelligenceAnalyzer()
analysis = await analyzer.analyze_events_forecast(
    historical_data=historical_data,
    recent_articles=recent_articles,
    days_ahead=7
)
```

**Manual Script:**
```python
analyzer = IntelligenceAnalyzer()
analysis = await analyzer.analyze_events_forecast(
    historical_data=historical_data,
    recent_articles=recent_articles,
    days_ahead=7
)
```

**Result:** ✅ **IDENTICAL**

---

### 4. Database INSERT - Identical ✅

**Scheduler:**
```python
store_query = """
    INSERT INTO ai_forecasts 
    (forecast_type, forecast_data, days_ahead, generated_at, valid_until, model_info)
    VALUES ($1, $2, $3, NOW(), $4, $5)
"""

async with pool.acquire() as conn:
    await conn.execute(
        store_query,
        'intelligence_forecast',
        json.dumps(analysis),
        7,
        valid_until,
        json.dumps(model_info)
    )
```

**Manual Script:**
```python
store_query = """
    INSERT INTO ai_forecasts 
    (forecast_type, forecast_data, days_ahead, generated_at, valid_until, model_info)
    VALUES ($1, $2, $3, NOW(), $4, $5)
"""

async with pool.acquire() as conn:
    await conn.execute(
        store_query,
        'intelligence_forecast',
        json.dumps(analysis),
        7,
        valid_until,
        json.dumps(model_info)
    )
```

**Result:** ✅ **IDENTICAL**

---

### 5. Trend Analysis - Identical ✅

**Scheduler:**
```python
store_query = """
    INSERT INTO ai_forecasts 
    (forecast_type, forecast_data, days_ahead, generated_at, valid_until, model_info)
    VALUES ($1, $2, $3, NOW(), $4, $5)
"""

async with pool.acquire() as conn:
    await conn.execute(
        store_query,
        'trend_analysis',
        json.dumps(analysis),
        30,  # trend analysis covers 30 days of historical data
        valid_until,
        json.dumps(model_info)
    )
```

**Manual Script:**
```python
store_query = """
    INSERT INTO ai_forecasts 
    (forecast_type, forecast_data, days_ahead, generated_at, valid_until, model_info)
    VALUES ($1, $2, $3, NOW(), $4, $5)
"""

async with pool.acquire() as conn:
    await conn.execute(
        store_query,
        'trend_analysis',
        json.dumps(analysis),
        30,
        valid_until,
        json.dumps(model_info)
    )
```

**Result:** ✅ **IDENTICAL**

---

## 📊 Summary Table

| Component | Scheduler | Manual Script | Match |
|-----------|-----------|---------------|-------|
| Historical Data Query | 60 days | 60 days | ✅ |
| Articles Query | 7 days, max 20 | 7 days, max 20 | ✅ |
| Data Processing | Same format | Same format | ✅ |
| AI Analysis Call | analyze_events_forecast | analyze_events_forecast | ✅ |
| INSERT Statement | Same columns | Same columns | ✅ |
| Parameter Order | $1, $2, $3, $4, $5 | $1, $2, $3, $4, $5 | ✅ |
| Trend Analysis | 30 days | 30 days | ✅ |
| Valid Until | NOW() + 8h | NOW() + 8h | ✅ |

---

## 🎯 Conclusion

**✅ YES - The code is 100% identical**

Both the scheduler and manual script:
1. ✅ Fetch the same data from the database
2. ✅ Process data in the same way
3. ✅ Call the same AI analysis functions
4. ✅ Insert into the database with identical SQL and parameters
5. ✅ Store all required fields (forecast_type, forecast_data, days_ahead, generated_at, valid_until, model_info)

**The only difference is:**
- Scheduler: Runs automatically every 10 hours
- Manual Script: Runs on-demand when you execute it

**Both produce identical results in the `ai_forecasts` table.**

---

## 🔄 Execution Flow Comparison

### Scheduler Flow
```
APScheduler (every 10 hours)
    ↓
_run_ai_forecast_sync()
    ↓
_run_ai_forecast()
    ↓
_generate_intelligence_forecast()  +  _generate_trend_analysis()
    ↓
INSERT INTO ai_forecasts
```

### Manual Script Flow
```
python scripts/generate_forecast_simple.py
    ↓
main()
    ↓
generate_intelligence_forecast()  +  generate_trend_analysis()
    ↓
INSERT INTO ai_forecasts
```

**Result:** ✅ **Same data in database**

---

## 💾 Database Records

Both methods create identical records:

```json
{
  "id": "auto-increment",
  "forecast_type": "intelligence_forecast",
  "forecast_data": { "complete JSON analysis" },
  "days_ahead": 7,
  "generated_at": "2026-03-09 14:33:02",
  "valid_until": "2026-03-09 22:33:02",
  "model_info": { "type", "model", "analyzed_at", "data_points", "news_analyzed" },
  "created_at": "2026-03-09 14:33:02"
}
```

---

## ✅ Verification

To verify both methods produce identical results:

```bash
# Run manual script
python scripts/generate_forecast_simple.py

# Check database
SELECT * FROM ai_forecasts ORDER BY generated_at DESC LIMIT 2;

# Compare with scheduler output (when it runs)
# Should see identical records
```
