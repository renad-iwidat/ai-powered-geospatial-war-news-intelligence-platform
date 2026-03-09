-- Migration: Add UNIQUE constraint on forecast_type for upsert operations
-- Purpose: Allow ON CONFLICT DO UPDATE to work properly
-- This ensures only one record per forecast_type exists

-- Add UNIQUE constraint if it doesn't exist
ALTER TABLE ai_forecasts
ADD CONSTRAINT unique_forecast_type UNIQUE (forecast_type);

-- Create unique index for faster lookups
CREATE UNIQUE INDEX IF NOT EXISTS idx_ai_forecasts_type_unique
ON ai_forecasts(forecast_type);

-- Comment
COMMENT ON CONSTRAINT unique_forecast_type ON ai_forecasts IS 'Ensures only one record per forecast type for upsert operations';
