/**
 * API Service Functions
 * Type-safe API calls to backend
 */

import apiClient from './api-client';
import type {
  NewsArticleListItem,
  GeographicLocationListItem,
  AnalyticsOverview,
  CountryStatistics,
  DateStatistics,
} from '@/types';

// News Articles
export const fetchLatestNews = async (limit: number = 20) => {
  const response = await apiClient.get<{ items: NewsArticleListItem[] }>(
    `/news-articles?limit=${limit}&offset=0`
  );
  return response.data.items;
};

// Geographic Locations
export const fetchLocations = async () => {
  const response = await apiClient.get<{ items: GeographicLocationListItem[] }>(
    '/geographic-locations'
  );
  return response.data.items;
};

export const fetchNewsByLocation = async (locationId: number) => {
  const response = await apiClient.get<{ items: NewsArticleListItem[] }>(
    `/geographic-locations/${locationId}/news?limit=50`
  );
  return response.data.items || [];
};

// Analytics
export const fetchAnalyticsOverview = async () => {
  const response = await apiClient.get<AnalyticsOverview>('/analytics/overview');
  return response.data;
};

export const fetchCountryStatistics = async () => {
  const response = await apiClient.get<{ countries: CountryStatistics[] }>(
    '/analytics/by-country'
  );
  return response.data.countries;
};

export const fetchDateStatistics = async (days: number = 30) => {
  const response = await apiClient.get<{ daily_stats: DateStatistics[] }>(
    `/analytics/by-date?days=${days}`
  );
  return response.data.daily_stats;
};

export const fetchMetricsBreakdown = async () => {
  const response = await apiClient.get<{ 
    metrics: Array<{
      metric_type: string;
      occurrences: number;
      total_value: number;
      average_value: number;
      max_value: number;
    }>;
    total_types: number;
  }>('/analytics/metrics-breakdown');
  return response.data;
};

export const fetchTopMetricsByCountry = async (limit: number = 10) => {
  const response = await apiClient.get<{
    metrics: Array<{
      metric_type: string;
      total_occurrences: number;
      overall_avg: number;
      overall_max: number;
      countries: Array<{
        country_code: string;
        occurrences: number;
        avg_value: number;
        max_value: number;
      }>;
    }>;
    total_types: number;
  }>(`/analytics/top-metrics-by-country?limit=${limit}`);
  return response.data;
};

export const fetchTopSources = async (limit: number = 10) => {
  const response = await apiClient.get<{
    sources: Array<{
      source_name: string;
      source_type: string;
      articles_count: number;
      events_count: number;
      percentage: number;
    }>;
    total_sources: number;
  }>(`/analytics/top-sources?limit=${limit}`);
  return response.data;
};

export const fetchHotLocations = async (limit: number = 15) => {
  const response = await apiClient.get<{
    locations: Array<{
      id: number;
      location_name: string;
      country_code: string;
      latitude: number;
      longitude: number;
      events_count: number;
      metrics_count: number;
      articles_count: number;
    }>;
    total_count: number;
  }>(`/analytics/hot-locations?limit=${limit}`);
  return response.data;
};

export const fetchMediaTypes = async () => {
  const response = await apiClient.get<{
    media_types: Array<{
      media_type: string;
      description: string;
      sources_count: number;
      articles_count: number;
      events_count: number;
      percentage: number;
    }>;
    total_types: number;
  }>('/analytics/media-types');
  return response.data;
};

export const fetchLanguageDistribution = async () => {
  const response = await apiClient.get<{
    languages: Array<{
      language_code: string;
      language_name: string;
      articles_count: number;
      events_count: number;
      translations_count: number;
      percentage: number;
    }>;
    total_languages: number;
  }>('/analytics/language-distribution');
  return response.data;
};

export const fetchActivityHeatmap = async (days: number = 30) => {
  const response = await apiClient.get<{
    heatmap_data: Array<{
      day_of_week: number;
      hour_of_day: number;
      articles_count: number;
      events_count: number;
    }>;
    days_analyzed: number;
  }>(`/analytics/activity-heatmap?days=${days}`);
  return response.data;
};

// Predictions & Forecasting
export const fetchEventsForecast = async (days: number = 7) => {
  const response = await apiClient.get<{
    predictions: Array<{
      date: string;
      predicted_value: number;
      lower_bound: number;
      upper_bound: number;
      confidence: number;
    }>;
    historical_data: Array<{
      date: string;
      count: number;
    }>;
    model_info: {
      type: string;
      trained_at: string | null;
      training_data_size: number;
      forecast_periods: number;
      confidence_interval: number;
    };
    accuracy_metrics?: {
      mae: number | null;
      mape: number | null;
      test_size?: number;
      message?: string;
    };
    disclaimer: {
      en: string;
      ar: string;
    };
  }>(`/predictions/events-forecast?days=${days}`);
  return response.data;
};

export const fetchTrendAnalysis = async () => {
  const response = await apiClient.get<{
    overall_trend: string;
    events_trend: string;
    articles_trend: string;
    change_percentage: number;
    recent_7_days_avg: number;
    previous_7_days_avg: number;
    analysis_period: {
      start_date: string;
      end_date: string;
      total_days: number;
    };
    interpretation: {
      en: string;
      ar: string;
    };
  }>('/predictions/trend-analysis');
  return response.data;
};

// AI-Powered Predictions
export const fetchAIIntelligenceForecast = async (days: number = 7) => {
  const response = await apiClient.get<{
    forecast: Array<{
      date: string;
      predicted_events: number;
      confidence: number;
    }>;
    trend: string;
    confidence_overall: number;
    key_factors: string[];
    risk_level: string;
    summary: {
      en: string;
      ar: string;
    };
    insights: {
      en: string;
      ar: string;
    };
    highest_risk_day?: {
      date: string;
      reason: string;
    };
    lowest_activity_day?: {
      date: string;
      reason: string;
    };
    model_info: {
      type: string;
      model: string;
      analyzed_at: string;
      data_points: number;
      news_analyzed: number;
    };
  }>(`/predictions/ai-intelligence-forecast?days=${days}`);
  return response.data;
};

export const fetchAITrendAnalysis = async () => {
  const response = await apiClient.get<{
    overall_trend: string;
    trend_strength: number;
    change_percentage: number;
    interpretation: {
      en: string;
      ar: string;
    };
    key_indicators: string[];
    next_7_days_outlook: {
      en: string;
      ar: string;
    };
  }>('/predictions/ai-trend-analysis');
  return response.data;
};

// Market Data
export const fetchMarketData = async () => {
  const response = await apiClient.get<{
    oil: {
      current: {
        price: number;
        date: string;
      } | null;
      trend: Array<{
        date: string;
        price: number;
      }>;
      change_7d: number | null;
      unit: string;
    };
    gold: {
      current: {
        price: number;
        date: string;
      } | null;
      unit: string;
    };
    analysis: {
      en: string;
      ar: string;
    };
  }>('/market-data/oil-gold-prices');
  return response.data;
};
