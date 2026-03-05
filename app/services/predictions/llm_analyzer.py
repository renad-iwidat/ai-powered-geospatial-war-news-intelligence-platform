"""
LLM-Based Intelligence Analysis Service
Uses OpenAI GPT to provide contextual war intelligence analysis
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import os
import certifi
from openai import OpenAI
from app.core.config import settings

class IntelligenceAnalyzer:
    """AI-powered intelligence analyzer for war events and predictions"""
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        # Fix SSL certificate issue on Windows
        os.environ['SSL_CERT_FILE'] = certifi.where()
        
        self.client = OpenAI(api_key=self.api_key)
    
    async def analyze_events_forecast(
        self,
        historical_data: List[Dict[str, Any]],
        recent_articles: List[Dict[str, Any]],
        days_ahead: int = 7
    ) -> Dict[str, Any]:
        """
        Generate intelligent forecast based on historical data and recent news
        
        Args:
            historical_data: List of daily event counts with dates
            recent_articles: Recent news articles with content
            days_ahead: Number of days to forecast
            
        Returns:
            Comprehensive analysis with predictions, confidence, and insights
        """
        
        # Prepare context for AI
        context = self._prepare_context(historical_data, recent_articles)
        
        # Create prompt
        prompt = f"""You are an expert geopolitical analyst specializing in Middle East conflicts and war intelligence.

HISTORICAL DATA (Last {len(historical_data)} days):
{json.dumps(historical_data, indent=2)}

RECENT NEWS CONTEXT:
{self._format_recent_news(recent_articles[:10])}

TASK:
Analyze the Iran war situation and provide:
1. Forecast for next {days_ahead} days (realistic event counts based on patterns)
2. Trend analysis (escalating, stable, or de-escalating)
3. Key factors influencing the situation
4. Confidence level (0-100%)
5. Risk assessment
6. Bilingual summary (English and Arabic)

IMPORTANT:
- Base predictions on actual data patterns
- Consider geopolitical context
- Be realistic and objective
- Provide specific numbers for daily forecasts
- Explain your reasoning

Return response in this JSON format:
{{
    "forecast": [
        {{"date": "YYYY-MM-DD", "predicted_events": <number>, "confidence": <0-100>}},
        ...
    ],
    "trend": "escalating|stable|de-escalating",
    "confidence_overall": <0-100>,
    "key_factors": ["factor1", "factor2", ...],
    "risk_level": "low|medium|high|critical",
    "summary": {{
        "en": "English summary...",
        "ar": "الملخص بالعربية..."
    }},
    "insights": {{
        "en": "Detailed English analysis...",
        "ar": "التحليل التفصيلي بالعربية..."
    }},
    "highest_risk_day": {{"date": "YYYY-MM-DD", "reason": "..."}},
    "lowest_activity_day": {{"date": "YYYY-MM-DD", "reason": "..."}}
}}
"""
        
        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional war intelligence analyst. Provide objective, data-driven analysis in JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for more consistent predictions
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            # Parse response
            analysis = json.loads(response.choices[0].message.content)
            
            # Add metadata
            analysis["model_info"] = {
                "type": "OpenAI GPT Intelligence Analysis",
                "model": self.model,
                "analyzed_at": datetime.utcnow().isoformat(),
                "data_points": len(historical_data),
                "news_analyzed": len(recent_articles)
            }
            
            return analysis
            
        except Exception as e:
            # Fallback to simple analysis if API fails
            return self._fallback_analysis(historical_data, days_ahead, str(e))
    
    async def analyze_trend(
        self,
        historical_data: List[Dict[str, Any]],
        recent_articles: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze current trend and provide strategic insights
        """
        
        prompt = f"""Analyze the current trend in the Iran war based on this data:

HISTORICAL DATA:
{json.dumps(historical_data[-14:], indent=2)}

RECENT NEWS:
{self._format_recent_news(recent_articles[:5])}

Provide trend analysis in JSON format:
{{
    "overall_trend": "escalating|stable|de-escalating",
    "trend_strength": <0-100>,
    "change_percentage": <number>,
    "interpretation": {{
        "en": "English interpretation...",
        "ar": "التفسير بالعربية..."
    }},
    "key_indicators": ["indicator1", "indicator2", ...],
    "next_7_days_outlook": {{
        "en": "English outlook...",
        "ar": "التوقعات بالعربية..."
    }}
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a war intelligence analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            return self._fallback_trend_analysis(historical_data, str(e))
    
    def _prepare_context(
        self,
        historical_data: List[Dict[str, Any]],
        recent_articles: List[Dict[str, Any]]
    ) -> str:
        """Prepare context string for AI analysis"""
        
        # Calculate statistics
        if historical_data:
            total_events = sum(d.get('count', 0) for d in historical_data)
            avg_events = total_events / len(historical_data)
            recent_avg = sum(d.get('count', 0) for d in historical_data[-7:]) / min(7, len(historical_data))
        else:
            total_events = avg_events = recent_avg = 0
        
        context = f"""
        Total Events: {total_events}
        Average Daily Events: {avg_events:.1f}
        Recent 7-Day Average: {recent_avg:.1f}
        Data Period: {len(historical_data)} days
        """
        
        return context
    
    def _format_recent_news(self, articles: List[Dict[str, Any]]) -> str:
        """Format recent news for AI context"""
        
        formatted = []
        for i, article in enumerate(articles[:10], 1):
            title = article.get('title', 'No title')
            content = article.get('content', '')[:200]  # First 200 chars
            date = article.get('published_at', 'Unknown date')
            
            formatted.append(f"{i}. [{date}] {title}\n   {content}...")
        
        return "\n\n".join(formatted)
    
    def _fallback_analysis(
        self,
        historical_data: List[Dict[str, Any]],
        days_ahead: int,
        error: str
    ) -> Dict[str, Any]:
        """Fallback analysis if API fails"""
        
        # Simple moving average
        if historical_data:
            recent_avg = sum(d.get('count', 0) for d in historical_data[-7:]) / min(7, len(historical_data))
        else:
            recent_avg = 0
        
        today = datetime.utcnow().date()
        forecast = []
        
        for i in range(1, days_ahead + 1):
            forecast_date = today + timedelta(days=i)
            forecast.append({
                "date": forecast_date.isoformat(),
                "predicted_events": int(recent_avg),
                "confidence": 50
            })
        
        return {
            "forecast": forecast,
            "trend": "stable",
            "confidence_overall": 50,
            "key_factors": ["Limited data available"],
            "risk_level": "medium",
            "summary": {
                "en": f"Basic forecast based on {len(historical_data)} days of data. API unavailable: {error}",
                "ar": f"توقعات أساسية بناءً على {len(historical_data)} يوم من البيانات. API غير متاح"
            },
            "insights": {
                "en": "Using simple moving average due to API limitations.",
                "ar": "استخدام المتوسط المتحرك البسيط بسبب قيود API"
            },
            "model_info": {
                "type": "Fallback Analysis",
                "error": error,
                "data_points": len(historical_data)
            }
        }
    
    def _fallback_trend_analysis(
        self,
        historical_data: List[Dict[str, Any]],
        error: str
    ) -> Dict[str, Any]:
        """Fallback trend analysis"""
        
        if len(historical_data) >= 14:
            recent_avg = sum(d.get('count', 0) for d in historical_data[-7:]) / 7
            previous_avg = sum(d.get('count', 0) for d in historical_data[-14:-7]) / 7
            change = ((recent_avg - previous_avg) / previous_avg * 100) if previous_avg > 0 else 0
            
            if change > 10:
                trend = "escalating"
            elif change < -10:
                trend = "de-escalating"
            else:
                trend = "stable"
        else:
            trend = "stable"
            change = 0
        
        return {
            "overall_trend": trend,
            "trend_strength": 50,
            "change_percentage": change,
            "interpretation": {
                "en": f"Trend is {trend} with {change:.1f}% change. API unavailable.",
                "ar": f"الاتجاه {trend} مع تغيير {change:.1f}٪. API غير متاح"
            },
            "key_indicators": ["Limited analysis available"],
            "error": error
        }
