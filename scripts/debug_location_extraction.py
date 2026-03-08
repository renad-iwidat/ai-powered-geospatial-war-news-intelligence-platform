#!/usr/bin/env python3
"""
Debug location extraction process
"""

import sys
import os
import asyncio

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.nlp.ner_simple import extract_places_simple
from app.services.geo.geocoder_geopy import get_geocoder

async def debug_extraction():
    """Debug the extraction process"""
    
    # Test texts from today's articles
    test_texts = [
        "الخليج في قلب المواجهة: بين الاستهداف الإيراني وتدويل المعادلة",
        "قيادي حوثي: نحن جاهزون وسنشارك عندما تطلب إيران من دمشق إلى بغداد",
        "من الحرب الدينية إلى تشكيل المنطقة: الحرب على إيران ستغير الشرق الأوسط",
        "إسرائيل تقصف مواقع عسكرية في سوريا والعراق",
        "مقتل 50 شخصاً في غارات جوية على صنعاء",
    ]
    
    print("🔍 Debugging Location Extraction")
    print("=" * 70)
    
    geocoder = get_geocoder()
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n📝 Test {i}: {text[:60]}...")
        print("-" * 70)
        
        # Step 1: Extract places
        print("  Step 1: Extracting places with NER...")
        try:
            places = extract_places_simple(text)
            print(f"    ✅ Found {len(places)} places:")
            for place in places:
                print(f"       - {place}")
        except Exception as e:
            print(f"    ❌ Error: {str(e)}")
            continue
        
        if not places:
            print("    ⚠️  No places found - skipping geocoding")
            continue
        
        # Step 2: Geocode each place
        print("  Step 2: Geocoding places...")
        for place in places[:3]:  # Limit to 3 per article
            try:
                result = await geocoder.geocode_place(place)
                if result:
                    print(f"    ✅ {place}:")
                    print(f"       - Country: {result.get('country_code')}")
                    print(f"       - Lat/Lng: ({result.get('lat')}, {result.get('lng')})")
                    print(f"       - OSM ID: {result.get('osm_id')}")
                    print(f"       - OSM Type: {result.get('osm_type')}")
                else:
                    print(f"    ❌ {place}: Not found")
            except Exception as e:
                print(f"    ❌ {place}: Error - {str(e)}")

if __name__ == "__main__":
    print("🧪 Testing Location Extraction Pipeline\n")
    asyncio.run(debug_extraction())
    print("\n✅ Debug completed")
