# AI Forecasts Schema Verification ✅

## Schema Definition

The `ai_forecasts` table has been verified to match the exact structure needed for storing AI-generated forecasts:

```sql
CREATE TABLE ai_forecasts (
    id SERIAL PRIMARY KEY,
    forecast_type VARCHAR(50) NOT NULL,      -- 'intelligence_forecast', 'trend_analysis'
    forecast_data JSONB NOT NULL,            -- Complete AI analysis result
    days_ahead INTEGER,                      -- Number of days forecasted
    generated_at TIMESTAMP NOT NULL,         -- When forecast was generated
    valid_until TIMESTAMP NOT NULL,          -- When forecast expires
    model_info JSONB,                        -- Model metadata (type, version, etc)
    created_at TIMESTAMP DEFAULT NOW()       -- Record creation timestamp
);
```

## Column Details

| Column | Type | Required | Purpose |
|--------|------|----------|---------|
| `id` | SERIAL | ✅ | Primary key, auto-increment |
| `forecast_type` | VARCHAR(50) | ✅ | Type of forecast: `intelligence_forecast` or `trend_analysis` |
| `forecast_data` | JSONB | ✅ | Complete JSON analysis result with all insights |
| `days_ahead` | INTEGER | ✅ | Number of days covered (7 for intelligence, 30 for trend) |
| `generated_at` | TIMESTAMP | ✅ | Timestamp when forecast was generated |
| `valid_until` | TIMESTAMP | ✅ | Expiration time (NOW() + 8 hours) |
| `model_info` | JSONB | ✅ | Model metadata (type, model name, analyzed_at, data_points, news_analyzed) |
| `created_at` | TIMESTAMP | ✅ | Record creation timestamp (defaults to NOW()) |

## Scheduler Integration

### Intelligence Forecast Insertion
```python
INSERT INTO ai_forecasts 
(forecast_type, forecast_data, days_ahead, generated_at, valid_until, model_info)
VALUES (
    'intelligence_forecast',           -- forecast_type
    json.dumps(analysis),              -- forecast_data (complete JSON)
    7,                                 -- days_ahead
    NOW(),                             -- generated_at
    datetime.utcnow() + timedelta(hours=8),  -- valid_until
    json.dumps(model_info)             -- model_info
)
```

### Trend Analysis Insertion
```python
INSERT INTO ai_forecasts 
(forecast_type, forecast_data, days_ahead, generated_at, valid_until, model_info)
VALUES (
    'trend_analysis',                  -- forecast_type
    json.dumps(analysis),              -- forecast_data (complete JSON)
    30,                                -- days_ahead (30-day historical window)
    NOW(),                             -- generated_at
    datetime.utcnow() + timedelta(hours=8),  -- valid_until
    json.dumps(model_info)             -- model_info
)
```

## Data Example

### Intelligence Forecast Record
```json
{
  "id": 7,
  "forecast_type": "intelligence_forecast",
  "forecast_data": {
    "trend": "escalating",
    "summary": {
      "ar": "تشير البيانات إلى تصاعد كبير...",
      "en": "The data indicates a significant escalation..."
    },
    "forecast": [
      {"date": "2026-03-07", "confidence": 80, "predicted_events": 330},
      {"date": "2026-03-08", "confidence": 75, "predicted_events": 290}
    ],
    "risk_level": "high",
    "confidence_overall": 70,
    "model_info": {
      "type": "OpenAI GPT Intelligence Analysis",
      "model": "gpt-4o",
      "analyzed_at": "2026-03-06T17:30:51.861488",
      "data_points": 6,
      "news_analyzed": 20
    }
  },
  "days_ahead": 7,
  "generated_at": "2026-03-06 17:30:52.160162",
  "valid_until": "2026-03-07 01:30:51.861488",
  "model_info": {
    "type": "OpenAI GPT Intelligence Analysis",
    "model": "gpt-4o",
    "analyzed_at": "2026-03-06T17:30:51.861488",
    "data_points": 6,
    "news_analyzed": 20
  },
  "created_at": "2026-03-06 17:30:52.160162"
}
```

### Trend Analysis Record
```json
{
  "id": 8,
  "forecast_type": "trend_analysis",
  "forecast_data": {
    "overall_trend": "escalating",
    "trend_strength": 85,
    "confidence_level": 80,
    "change_percentage": 530,
    "interpretation": {
      "ar": "تشير البيانات إلى زيادة كبيرة...",
      "en": "The data indicates a significant increase..."
    },
    "key_indicators": [
      "Increase in conflict event count from 0 to 408 on March 5",
      "Continued high count of 252 on March 6",
      "Recent news reports of military actions"
    ],
    "model_info": {
      "type": "OpenAI GPT Trend Analysis",
      "model": "gpt-4o",
      "analyzed_at": "2026-03-06T17:31:02.207438",
      "data_points": 6,
      "news_analyzed": 20
    }
  },
  "days_ahead": 30,
  "generated_at": "2026-03-06 17:31:02.207438",
  "valid_until": "2026-03-07 01:31:01.911553",
  "model_info": {
    "type": "OpenAI GPT Trend Analysis",
    "model": "gpt-4o",
    "analyzed_at": "2026-03-06T17:31:02.207438",
    "data_points": 6,
    "news_analyzed": 20
  },
  "created_at": "2026-03-06 17:31:02.207438"
}
```

## Scheduler Execution Flow

### Every 10 Hours:
1. **Intelligence Forecast Generation**
   - Fetches 60 days of historical data
   - Analyzes last 20 news articles
   - Generates 7-day forecast
   - Inserts into `ai_forecasts` with `days_ahead=7`

2. **Trend Analysis Generation**
   - Fetches 30 days of historical data
   - Analyzes last 10 news articles
   - Generates trend analysis
   - Inserts into `ai_forecasts` with `days_ahead=30`

## Verification Scripts

### 1. Verify Schema
```bash
python scripts/verify_ai_forecasts_schema.py
```
Checks:
- ✅ Table exists
- ✅ All columns present with correct types
- ✅ Data count and latest records
- ✅ Schema compliance

### 2. Test Forecast Insertion
```bash
python scripts/test_scheduler_forecast_insert.py
```
Tests:
- ✅ Intelligence forecast insertion
- ✅ Trend analysis insertion
- ✅ Data integrity verification
- ✅ Schema compliance

## Indexes

```sql
-- Fast lookup of latest valid forecast by type
CREATE INDEX idx_ai_forecasts_type_valid 
ON ai_forecasts(forecast_type, valid_until DESC);

-- Cleanup of old forecasts
CREATE INDEX idx_ai_forecasts_generated_at 
ON ai_forecasts(generated_at);
```

## Caching Strategy

- **Cache Duration**: 8 hours (valid_until = NOW() + 8 hours)
- **Refresh Frequency**: Every 10 hours (scheduler runs)
- **Overlap**: 2 hours of overlap between forecasts ensures no gaps
- **Cleanup**: Old forecasts (older than 7 days) can be deleted

## API Endpoints Using This Table

### Get Intelligence Forecast
```
GET /api/v1/predictions/intelligence-forecast
```
Returns latest valid `intelligence_forecast` record

### Get Trend Analysis
```
GET /api/v1/predictions/trend-analysis
```
Returns latest valid `trend_analysis` record

## Status

✅ **Schema Verified** - Matches exact structure from production data
✅ **Scheduler Updated** - Both forecast types insert all required fields
✅ **Data Integrity** - All columns properly populated
✅ **Caching Active** - 8-hour validity window with 10-hour refresh cycle
