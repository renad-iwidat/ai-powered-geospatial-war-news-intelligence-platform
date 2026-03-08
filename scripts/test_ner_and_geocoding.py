#!/usr/bin/env python3
"""
Test NER and Geocoding functionality
"""

import sys
import os

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.nlp.ner_camel import extract_places_ner
from app.services.geo.geocoder_geopy import get_geocoder
import asyncio

def test_ner():
    """Test NER extraction"""
    print("🧪 Testing NER (Named Entity Recognition)")
    print("=" * 60)
    
    test_texts = [
        "الخليج في قلب المواجهة: بين الاستهداف الإيراني وتدويل المعادلة",
        "قيادي حوثي: نحن جاهزون وسنشارك عندما تطلب إيران من دمشق إلى بغداد",
        "من الحرب الدينية إلى تشكيل المنطقة: الحرب على إيران ستغير الشرق الأوسط",
        "إسرائيل تقصف مواقع عسكرية في سوريا والعراق",
        "مقتل 50 شخصاً في غارات جوية على صنعاء",
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n📝 Test {i}: {text[:60]}...")
        try:
            places = extract_places_ner(text)
            if places:
                print(f"   ✅ Found {len(places)} places:")
                for place in places:
                    print(f"      - {place}")
            else:
                print(f"   ❌ No places found")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

async def test_geocoding():
    """Test geocoding"""
    print("\n\n🧪 Testing Geocoding")
    print("=" * 60)
    
    test_places = [
        "إيران",
        "العراق",
        "سوريا",
        "دمشق",
        "بغداد",
        "طهران",
        "صنعاء",
        "الخليج",
    ]
    
    geocoder = get_geocoder()
    
    for place in test_places:
        print(f"\n📍 Geocoding: {place}")
        try:
            result = await geocoder.geocode_place(place)
            if result:
                print(f"   ✅ Found:")
                print(f"      - Country: {result.get('country_code')}")
                print(f"      - Coordinates: ({result.get('lat')}, {result.get('lng')})")
                print(f"      - Display: {result.get('display_name')[:60]}...")
            else:
                print(f"   ❌ Not found")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

if __name__ == "__main__":
    print("🔍 Testing NER and Geocoding Services\n")
    
    test_ner()
    asyncio.run(test_geocoding())
    
    print("\n\n✅ Tests completed")
