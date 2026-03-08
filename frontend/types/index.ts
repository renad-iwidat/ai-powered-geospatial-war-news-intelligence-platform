/**
 * TypeScript Type Definitions
 * Matching backend Pydantic schemas
 */

export interface NewsArticleListItem {
  id: number;
  title: string;
  content_preview: string | null;
  content: string | null;
  url: string;
  source_name: string | null;
  language_code: string;
  published_at: string | null;
  has_numbers: boolean;
  events_count: number;
  metrics_count: number;
}

export interface GeographicLocationListItem {
  id: number;
  name: string;
  country_code: string;
  latitude: number;
  longitude: number;
  events_count: number;
}

export interface AnalyticsOverview {
  total_news_articles: number;
  total_locations: number;
  total_events: number;
  total_metrics: number;
  total_countries: number;
  articles_with_events: number;
  articles_without_events: number;
  events_with_metrics: number;
  events_without_metrics: number;
}

export interface CountryStatistics {
  country_code: string;
  country_name: string | null;
  locations_count: number;
  events_count: number;
  metrics_count: number;
}

export interface DateStatistics {
  date: string;
  articles_count: number;
  events_count: number;
  metrics_count: number;
}

export type Language = 'en' | 'ar';
