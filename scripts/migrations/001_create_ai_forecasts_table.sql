-- Migration: Create ai_forecasts table for caching AI analysis
-- Purpose: Store AI-generated forecasts to reduce API costs
-- Schedule: Run twice daily (1 PM and 9 PM Palestine time)

CREATE TABLE IF NOT EXISTS ai_forecasts (
    id SERIAL PRIMARY KEY,
    forecast_type VARCHAR(50) NOT NULL UNIQUE,  -- 'events_forecast', 'trend_analysis', 'intelligence_forecast'
    forecast_data JSONB NOT NULL,        -- The complete AI analysis result
    days_ahead INTEGER,                  -- Number of days forecasted (for forecast types)
    generated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    valid_until TIMESTAMP NOT NULL,      -- When this forecast expires
    model_info JSONB,                    -- Model metadata (type, version, etc)
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index for fast lookup of latest valid forecast
CREATE INDEX IF NOT EXISTS idx_ai_forecasts_type_valid 
ON ai_forecasts(forecast_type, valid_until DESC);

-- Index for cleanup of old forecasts
CREATE INDEX IF NOT EXISTS idx_ai_forecasts_generated_at 
ON ai_forecasts(generated_at);

-- Unique constraint on forecast_type for upsert operations
CREATE UNIQUE INDEX IF NOT EXISTS idx_ai_forecasts_type_unique
ON ai_forecasts(forecast_type);

-- Comments
COMMENT ON TABLE ai_forecasts IS 'Cached AI-generated forecasts and analysis to reduce API costs';
COMMENT ON COLUMN ai_forecasts.forecast_type IS 'Type: events_forecast, trend_analysis, intelligence_forecast';
COMMENT ON COLUMN ai_forecasts.forecast_data IS 'Complete JSON response from AI analysis';
COMMENT ON COLUMN ai_forecasts.valid_until IS 'Forecast expires after this time (next scheduled run)';
