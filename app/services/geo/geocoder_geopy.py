"""
Geocoding Service using geopy
Converts place names to geographic coordinates
"""

from typing import Optional, Dict
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import asyncio
from functools import partial

from app.core.config import settings


class GeocoderService:
    """Geocoding service using geopy with Nominatim"""
    
    def __init__(self):
        self.geolocator = Nominatim(
            user_agent=settings.GEOCODING_USER_AGENT,
            timeout=10
        )
        # Rate limiter: 1 request per second
        self.geocode = RateLimiter(
            lambda query: self.geolocator.geocode(query, addressdetails=True),
            min_delay_seconds=1.0
        )
    
    async def geocode_place(self, place_name: str) -> Optional[Dict]:
        """
        Geocode a place name to coordinates
        
        Args:
            place_name: Name of the place to geocode
        
        Returns:
            Dictionary with:
            - lat: Latitude
            - lng: Longitude
            - country_code: Country code (e.g., 'SY', 'IQ')
            - display_name: Full place name
            - osm_id: OpenStreetMap ID
            - osm_type: OSM type (node, way, relation)
            
            Or None if not found
        """
        try:
            # Run geocoding in thread pool (geopy is sync)
            loop = asyncio.get_event_loop()
            location = await loop.run_in_executor(
                None,
                partial(self.geocode, place_name)
            )
            
            if not location:
                return None
            
            # Extract data from raw response
            country_code = None
            osm_id = None
            osm_type = None
            
            if hasattr(location, 'raw'):
                raw = location.raw
                
                # Try to get country code from address field first
                if 'address' in raw:
                    country_code = raw['address'].get('country_code', '').upper()
                
                # If not found, try display_name parsing (fallback)
                # Most locations should have address field though
                
                # Extract OSM data
                osm_id = raw.get('osm_id')
                osm_type = raw.get('osm_type')
            
            # We need at least OSM data to store the location
            if not osm_id or not osm_type:
                return None
            
            return {
                "lat": location.latitude,
                "lng": location.longitude,
                "country_code": country_code or "UNKNOWN",
                "display_name": location.address,
                "osm_id": int(osm_id) if osm_id else None,
                "osm_type": osm_type
            }
            
        except (GeocoderTimedOut, GeocoderServiceError):
            return None
        except Exception:
            return None


# Global geocoder instance
_geocoder = None

def get_geocoder() -> GeocoderService:
    """Get or create geocoder instance"""
    global _geocoder
    if _geocoder is None:
        _geocoder = GeocoderService()
    return _geocoder
