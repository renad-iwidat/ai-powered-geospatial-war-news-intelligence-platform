"""
Predictions & Forecasting Endpoints
AI-powered predictions based on historical data
"""

from fastapi import APIRouter, Query, Depends, HTTPException
from datetime import date, timedelta, datetime, timezone
import asyncpg
import logging
import json

from app.core.database import get_db_pool
from app.core.config import settings
from app.services.predictions import TimeSeriesForecaster, SimpleTrendAnalyzer
from app.services.predictions.llm_analyzer import IntelligenceAnalyzer

router = APIRouter()
logger = logging.getLogger(__name__)


# ============================================================================
# Helper Functions for Cached Forecasts
# ============================================================================

async def get_cached_forecast(
    pool: asyncpg.Pool,
    forecast_type: str
) -> dict:
    """
    Get cached forecast from database if available and valid
    
    Returns None if no valid cache exists
    """
    query = """
        SELECT forecast_data, generated_at, valid_until
        FROM ai_forecasts
        WHERE forecast_type = $1
            AND valid_until > NOW()
        ORDER BY generated_at DESC
        LIMIT 1
    """
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, forecast_type)
    
    if row:
        forecast_data = json.loads(row['forecast_data']) if isinstance(row['forecast_data'], str) else row['forecast_data']
        
        # Add cache metadata
        forecast_data['cache_info'] = {
            'cached': True,
            'generated_at': row['generated_at'].isoformat(),
            'valid_until': row['valid_until'].isoformat(),
            'note': {
                'en': 'This is a cached forecast generated at scheduled time to reduce API costs.',
                'ar': 'هذا توقع محفوظ تم إنشاؤه في الوقت المحدد لتقليل تكاليف API.'
            }
        }
        
        return forecast_data
    
    return None


@router.get("/events-forecast")
async def forecast_events(
    days: int = Query(7, ge=1, le=30, description="Number of days to forecast"),
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """
    Forecast future events count using time series analysis
    
    - **days**: Number of days to forecast (1-30)
    
    Returns predictions with confidence intervals
    
    **Note**: These are probabilistic predictions based on historical patterns,
    not deterministic forecasts.
    """
    
    try:
        # Fetch historical data
        query = """
            SELECT
                DATE(COALESCE(rn.published_at, rn.fetched_at)) as date,
                COUNT(DISTINCT ne.id) as count
            FROM raw_news rn
            LEFT JOIN news_events ne ON rn.id = ne.raw_news_id
            WHERE COALESCE(rn.published_at, rn.fetched_at) >= CURRENT_DATE - INTERVAL '90 days'
            GROUP BY DATE(COALESCE(rn.published_at, rn.fetched_at))
            ORDER BY date ASC
        """
        
        async with pool.acquire() as conn:
            rows = await conn.fetch(query)
        
        if len(rows) < 7:
            # Use simple moving average for small datasets
            historical_data = [{'date': row['date'], 'count': row['count']} for row in rows]
            result = SimpleTrendAnalyzer.moving_average_forecast(historical_data, periods=days)
            result['historical_data'] = historical_data
            result['disclaimer'] = {
                'en': 'Limited historical data available. Predictions are based on simple moving average.',
                'ar': 'بيانات تاريخية محدودة متاحة. التوقعات مبنية على المتوسط المتحرك البسيط.'
            }
            result['warning'] = {
                'en': f'Only {len(rows)} days of data available. More data needed for accurate predictions.',
                'ar': f'فقط {len(rows)} أيام من البيانات متاحة. نحتاج المزيد من البيانات للتوقعات الدقيقة.'
            }
            return result
        
        historical_data = [{'date': row['date'], 'count': row['count']} for row in rows]
        
        # Try Prophet first, fallback to simple MA
        try:
            forecaster = TimeSeriesForecaster()
            df = forecaster.prepare_data(historical_data)
            forecaster.train_model(df)
            forecast_df = forecaster.forecast(periods=days)
            result = forecaster.get_forecast_summary(forecast_df, periods=days)
            
            # Add accuracy metrics
            accuracy = forecaster.calculate_accuracy_metrics(df)
            result['accuracy_metrics'] = accuracy
            
        except ImportError:
            logger.warning("Prophet not available, using simple moving average")
            result = SimpleTrendAnalyzer.moving_average_forecast(historical_data, periods=days)
        
        # Add historical data for comparison
        result['historical_data'] = historical_data[-30:]  # Last 30 days
        
        # Add disclaimer
        result['disclaimer'] = {
            'en': 'These predictions are probabilistic estimates based on historical patterns and should not be considered as definitive forecasts.',
            'ar': 'هذه التوقعات هي تقديرات احتمالية مبنية على الأنماط التاريخية ولا ينبغي اعتبارها توقعات نهائية.'
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Error in events forecast: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/articles-forecast")
async def forecast_articles(
    days: int = Query(7, ge=1, le=30, description="Number of days to forecast"),
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """
    Forecast future articles count
    
    - **days**: Number of days to forecast (1-30)
    
    Returns predictions for daily article volume
    """
    
    try:
        # Fetch historical data
        query = """
            SELECT
                DATE(COALESCE(published_at, fetched_at)) as date,
                COUNT(*) as count
            FROM raw_news
            WHERE COALESCE(published_at, fetched_at) >= CURRENT_DATE - INTERVAL '90 days'
            GROUP BY DATE(COALESCE(published_at, fetched_at))
            ORDER BY date ASC
        """
        
        async with pool.acquire() as conn:
            rows = await conn.fetch(query)
        
        if len(rows) < 7:
            # Use simple moving average for small datasets
            historical_data = [{'date': row['date'], 'count': row['count']} for row in rows]
            result = SimpleTrendAnalyzer.moving_average_forecast(historical_data, periods=days)
            result['historical_data'] = historical_data
            result['disclaimer'] = {
                'en': 'Limited historical data available. Predictions are based on simple moving average.',
                'ar': 'بيانات تاريخية محدودة متاحة. التوقعات مبنية على المتوسط المتحرك البسيط.'
            }
            result['warning'] = {
                'en': f'Only {len(rows)} days of data available. More data needed for accurate predictions.',
                'ar': f'فقط {len(rows)} أيام من البيانات متاحة. نحتاج المزيد من البيانات للتوقعات الدقيقة.'
            }
            return result
        
        historical_data = [{'date': row['date'], 'count': row['count']} for row in rows]
        
        # Try Prophet first
        try:
            forecaster = TimeSeriesForecaster()
            df = forecaster.prepare_data(historical_data)
            forecaster.train_model(df)
            forecast_df = forecaster.forecast(periods=days)
            result = forecaster.get_forecast_summary(forecast_df, periods=days)
            
            accuracy = forecaster.calculate_accuracy_metrics(df)
            result['accuracy_metrics'] = accuracy
            
        except ImportError:
            result = SimpleTrendAnalyzer.moving_average_forecast(historical_data, periods=days)
        
        result['historical_data'] = historical_data[-30:]
        result['disclaimer'] = {
            'en': 'Predictions are based on historical patterns and may not reflect sudden changes in news coverage.',
            'ar': 'التوقعات مبنية على الأنماط التاريخية وقد لا تعكس التغيرات المفاجئة في التغطية الإخبارية.'
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Error in articles forecast: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trend-analysis")
async def analyze_trend(
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """
    Analyze overall trend direction
    
    Returns whether the situation is escalating, stable, or de-escalating
    based on recent data patterns
    """
    
    try:
        # Fetch recent data
        query = """
            SELECT
                DATE(COALESCE(rn.published_at, rn.fetched_at)) as date,
                COUNT(DISTINCT ne.id) as events_count,
                COUNT(DISTINCT rn.id) as articles_count,
                COUNT(DISTINCT em.id) as metrics_count
            FROM raw_news rn
            LEFT JOIN news_events ne ON rn.id = ne.raw_news_id
            LEFT JOIN event_metrics em ON ne.id = em.event_id
            WHERE COALESCE(rn.published_at, rn.fetched_at) >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY DATE(COALESCE(rn.published_at, rn.fetched_at))
            ORDER BY date ASC
        """
        
        async with pool.acquire() as conn:
            rows = await conn.fetch(query)
        
        if len(rows) < 14:
            return {
                'trend': 'insufficient_data',
                'message': 'Not enough data for trend analysis',
                'days_available': len(rows)
            }
        
        # Analyze events trend
        events_data = [{'date': row['date'], 'count': row['events_count']} for row in rows]
        events_trend = SimpleTrendAnalyzer.calculate_trend(events_data)
        
        # Analyze articles trend
        articles_data = [{'date': row['date'], 'count': row['articles_count']} for row in rows]
        articles_trend = SimpleTrendAnalyzer.calculate_trend(articles_data)
        
        # Calculate recent vs older averages
        recent_7_days = rows[-7:]
        older_7_days = rows[-14:-7]
        
        recent_avg_events = sum(r['events_count'] for r in recent_7_days) / 7
        older_avg_events = sum(r['events_count'] for r in older_7_days) / 7
        
        change_pct = ((recent_avg_events - older_avg_events) / (older_avg_events + 1)) * 100
        
        return {
            'overall_trend': events_trend,
            'events_trend': events_trend,
            'articles_trend': articles_trend,
            'change_percentage': round(change_pct, 2),
            'recent_7_days_avg': round(recent_avg_events, 2),
            'previous_7_days_avg': round(older_avg_events, 2),
            'analysis_period': {
                'start_date': rows[0]['date'].isoformat(),
                'end_date': rows[-1]['date'].isoformat(),
                'total_days': len(rows)
            },
            'interpretation': {
                'en': f"The situation is currently {events_trend.replace('_', ' ')} with a {abs(change_pct):.1f}% {'increase' if change_pct > 0 else 'decrease'} in events over the past week.",
                'ar': f"الوضع حالياً {_translate_trend_ar(events_trend)} مع {'زيادة' if change_pct > 0 else 'انخفاض'} بنسبة {abs(change_pct):.1f}% في الأحداث خلال الأسبوع الماضي."
            }
        }
        
    except Exception as e:
        logger.error(f"Error in trend analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/country-forecast")
async def forecast_by_country(
    country_code: str = Query(..., description="Country code (e.g., PS, IQ)"),
    days: int = Query(7, ge=1, le=30, description="Number of days to forecast"),
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """
    Forecast events for a specific country
    
    - **country_code**: ISO country code
    - **days**: Number of days to forecast
    
    Returns country-specific predictions
    """
    
    try:
        query = """
            SELECT
                DATE(COALESCE(rn.published_at, rn.fetched_at)) as date,
                COUNT(DISTINCT ne.id) as count
            FROM raw_news rn
            JOIN news_events ne ON rn.id = ne.raw_news_id
            JOIN locations l ON ne.location_id = l.id
            WHERE l.country_code = $1
                AND COALESCE(rn.published_at, rn.fetched_at) >= CURRENT_DATE - INTERVAL '90 days'
            GROUP BY DATE(COALESCE(rn.published_at, rn.fetched_at))
            ORDER BY date ASC
        """
        
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, country_code.upper())
        
        if len(rows) < 7:
            return {
                'error': 'insufficient_data',
                'message': f'Not enough data for country {country_code}',
                'days_available': len(rows)
            }
        
        historical_data = [{'date': row['date'], 'count': row['count']} for row in rows]
        
        # Use simple MA for country-specific forecasts
        result = SimpleTrendAnalyzer.moving_average_forecast(historical_data, periods=days)
        result['country_code'] = country_code.upper()
        result['historical_data'] = historical_data[-30:]
        
        return result
        
    except Exception as e:
        logger.error(f"Error in country forecast: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def _translate_trend_ar(trend: str) -> str:
    """Helper to translate trend to Arabic"""
    translations = {
        'escalating': 'في تصعيد',
        'stable': 'مستقر',
        'de-escalating': 'في تهدئة',
        'insufficient_data': 'بيانات غير كافية'
    }
    return translations.get(trend, trend)


@router.get("/ai-intelligence-forecast")
async def ai_intelligence_forecast(
    days: int = Query(7, ge=1, le=14, description="Number of days to forecast"),
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """
    🤖 AI-Powered Intelligence Forecast (READ-ONLY)
    
    Returns cached forecasts generated by the scheduler.
    The scheduler generates forecasts twice daily (1 PM and 9 PM Palestine time).
    
    **Note**: This endpoint reads from the database only.
    New forecasts are generated by the background scheduler.
    """
    
    try:
        # Read from database only
        query = """
            SELECT forecast_data, generated_at, valid_until
            FROM ai_forecasts
            WHERE forecast_type = 'intelligence_forecast'
            ORDER BY generated_at DESC
            LIMIT 1
        """
        
        async with pool.acquire() as conn:
            row = await conn.fetchrow(query)
        
        if not row:
            return {
                'error': 'no_forecast_available',
                'message': {
                    'en': 'No forecast available yet. The scheduler generates forecasts twice daily.',
                    'ar': 'لا يوجد توقع متاح حالياً. يولد الجدولة التوقعات مرتين يومياً.'
                }
            }
        
        forecast_data = json.loads(row['forecast_data']) if isinstance(row['forecast_data'], str) else row['forecast_data']
        
        # Check if forecast is old (not from today)
        generated_date = row['generated_at'].date()
        today = datetime.now(timezone.utc).date()
        is_old = generated_date < today
        
        forecast_data['cache_info'] = {
            'cached': True,
            'generated_at': row['generated_at'].isoformat(),
            'valid_until': row['valid_until'].isoformat(),
            'is_old': is_old,
            'note': {
                'en': 'This forecast was generated by the scheduler. It may be outdated.' if is_old else 'This forecast was generated today by the scheduler.',
                'ar': 'تم إنشاء هذا التوقع بواسطة الجدولة. قد يكون قديماً.' if is_old else 'تم إنشاء هذا التوقع اليوم بواسطة الجدولة.'
            }
        }
        
        return forecast_data
        
    except Exception as e:
        logger.error(f"Error reading intelligence forecast: {str(e)}")
        return {
            'error': 'database_error',
            'message': {
                'en': f'Error reading forecast: {str(e)}',
                'ar': f'خطأ في قراءة التوقع: {str(e)}'
            }
        }


@router.get("/ai-trend-analysis")
async def ai_trend_analysis(
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """
    🤖 AI-Powered Trend Analysis (READ-ONLY)
    
    Returns cached trend analysis generated by the scheduler.
    The scheduler generates analysis twice daily (1 PM and 9 PM Palestine time).
    
    **Note**: This endpoint reads from the database only.
    New analysis is generated by the background scheduler.
    """
    
    try:
        # Read from database only
        query = """
            SELECT forecast_data, generated_at, valid_until
            FROM ai_forecasts
            WHERE forecast_type = 'trend_analysis'
            ORDER BY generated_at DESC
            LIMIT 1
        """
        
        async with pool.acquire() as conn:
            row = await conn.fetchrow(query)
        
        if not row:
            return {
                'error': 'no_analysis_available',
                'message': {
                    'en': 'No trend analysis available yet. The scheduler generates analysis twice daily.',
                    'ar': 'لا يوجد تحليل اتجاه متاح حالياً. تولد الجدولة التحليل مرتين يومياً.'
                }
            }
        
        analysis = json.loads(row['forecast_data']) if isinstance(row['forecast_data'], str) else row['forecast_data']
        
        # Check if analysis is old (not from today)
        generated_date = row['generated_at'].date()
        today = datetime.now(timezone.utc).date()
        is_old = generated_date < today
        
        analysis['cache_info'] = {
            'cached': True,
            'generated_at': row['generated_at'].isoformat(),
            'valid_until': row['valid_until'].isoformat(),
            'is_old': is_old,
            'note': {
                'en': 'This analysis was generated by the scheduler. It may be outdated.' if is_old else 'This analysis was generated today by the scheduler.',
                'ar': 'تم إنشاء هذا التحليل بواسطة الجدولة. قد يكون قديماً.' if is_old else 'تم إنشاء هذا التحليل اليوم بواسطة الجدولة.'
            }
        }
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error reading trend analysis: {str(e)}")
        return {
            'error': 'database_error',
            'message': {
                'en': f'Error reading analysis: {str(e)}',
                'ar': f'خطأ في قراءة التحليل: {str(e)}'
            }
        }
