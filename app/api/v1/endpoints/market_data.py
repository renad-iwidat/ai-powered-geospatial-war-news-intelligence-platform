"""
Market Data Endpoints
Oil & Gold prices from Yahoo Finance API
"""

from fastapi import APIRouter
import requests
import logging
from datetime import datetime, timedelta
import time

router = APIRouter()
logger = logging.getLogger(__name__)

BASE_URL = "https://query1.finance.yahoo.com/v8/finance/chart"

# Headers to avoid being blocked
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# Cache storage with timestamp
_cache = {
    "data": None,
    "timestamp": 0,
    "ttl": 500  # 1 minute cache - reduced to get fresher data
}


def fetch_asset(symbol: str):
    """
    Fetch asset data from Yahoo Finance
    
    Args:
        symbol: GC=F (Gold Futures), CL=F (WTI Oil), or BZ=F (Brent Oil)
    
    Returns:
        dict with current price, 7-day trend, and % change
    """
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            # Use hourly data for better accuracy
            url = f"{BASE_URL}/{symbol}?range=7d&interval=1h"
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            result = data["chart"]["result"][0]
            
            # Extract close prices and timestamps
            prices = result["indicators"]["quote"][0]["close"]
            timestamps = result["timestamp"]
            
            # Build trend with valid prices only
            trend = []
            for t, p in zip(timestamps, prices):
                if p is not None:
                    trend.append({
                        "timestamp": t,
                        "date": datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M'),
                        "price": round(p, 2)
                    })
            
            if not trend:
                raise ValueError(f"No valid price data for {symbol}")
            
            # Calculate current price and 7-day change
            current_price = trend[-1]["price"]
            first_price = trend[0]["price"]
            change_7d = round((current_price - first_price) / first_price * 100, 2)
            
            return {
                "current": {
                    "price": current_price,
                    "date": trend[-1]["date"]
                },
                "trend": trend,
                "change_7d": change_7d
            }
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Too Many Requests
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"Rate limited for {symbol}. Retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"Rate limited for {symbol} after {max_retries} attempts")
                    raise
            else:
                logger.error(f"HTTP Error fetching {symbol}: {str(e)}")
                raise
        except Exception as e:
            logger.error(f"Error fetching {symbol} from Yahoo Finance: {str(e)}")
            raise
    
    raise Exception(f"Failed to fetch {symbol} after {max_retries} attempts")


@router.get("/oil-gold-prices")
async def get_oil_gold_prices():
    """
    Get current Oil and Gold prices from Yahoo Finance
    
    Uses:
    - GC=F (Gold Futures - COMEX)
    - CL=F (WTI Crude Oil - NYMEX)
    
    Returns latest prices, 7-day hourly trend, and % change
    Cached for 5 minutes
    """
    
    try:
        # Check cache
        current_time = time.time()
        if _cache["data"] and (current_time - _cache["timestamp"]) < _cache["ttl"]:
            logger.info("Returning cached market data")
            return _cache["data"]
        
        # Fetch fresh data
        logger.info("Fetching fresh market data from Yahoo Finance")
        
        gold_data = fetch_asset("GC=F")
        oil_data = fetch_asset("CL=F")
        
        response = {
            "gold": {
                "current": gold_data["current"],
                "trend": gold_data["trend"],
                "change_7d": gold_data["change_7d"],
                "unit": "USD/oz",
                "symbol": "GC=F"
            },
            "oil": {
                "current": oil_data["current"],
                "trend": oil_data["trend"],
                "change_7d": oil_data["change_7d"],
                "unit": "USD/barrel",
                "symbol": "CL=F"
            },
            "analysis": {
                "en": f"Gold prices {'increased' if gold_data['change_7d'] > 0 else 'decreased'} by {abs(gold_data['change_7d']):.1f}% over the last 7 days. Oil prices {'increased' if oil_data['change_7d'] > 0 else 'decreased'} by {abs(oil_data['change_7d']):.1f}%. This {'may indicate increased' if oil_data['change_7d'] > 0 else 'suggests reduced'} geopolitical tensions.",
                "ar": f"أسعار الذهب {'ارتفعت' if gold_data['change_7d'] > 0 else 'انخفضت'} بنسبة {abs(gold_data['change_7d']):.1f}٪ خلال آخر 7 أيام. أسعار النفط {'ارتفعت' if oil_data['change_7d'] > 0 else 'انخفضت'} بنسبة {abs(oil_data['change_7d']):.1f}٪. هذا {'قد يشير إلى زيادة' if oil_data['change_7d'] > 0 else 'يشير إلى انخفاض'} التوترات الجيوسياسية."
            }
        }
        
        # Update cache
        _cache["data"] = response
        _cache["timestamp"] = current_time
        
        return response
        
    except Exception as e:
        logger.error(f"Error in get_oil_gold_prices: {str(e)}")
        
        # Return cached data if available, otherwise raise error
        if _cache["data"]:
            logger.info("Returning previously cached data due to fetch error")
            return _cache["data"]
        
        # No cache available - raise error to client
        raise
