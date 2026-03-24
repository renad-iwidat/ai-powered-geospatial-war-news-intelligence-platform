#!/usr/bin/env python3
"""
Test script for hardcoded locations processing
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.geo.location_processor import (
    find_locations_in_text,
    LOCATIONS_DATABASE,
    split_prefix_if_safe
)


def test_find_locations():
    """Test finding locations in text"""
    
    test_cases = [
        {
            "text": "حدث انفجار في بيروت وأثر على دمشق",
            "expected": ["بيروت", "دمشق"]
        },
        {
            "text": "الأخبار من الرياض والقاهرة تشير إلى تطورات جديدة",
            "expected": ["الرياض", "القاهرة"]
        },
        {
            "text": "وبغداد وطهران يناقشان الأوضاع",
            "expected": ["بغداد", "طهران"]
        },
        {
            "text": "لبنان وسوريا والعراق يعقدون اجتماعات",
            "expected": ["لبنان", "سوريا", "العراق"]
        },
        {
            "text": "في إسطنبول وأنقرة تم توقيع اتفاقية",
            "expected": ["إسطنبول", "أنقرة"]
        }
    ]
    
    print("=" * 80)
    print("Testing Location Finding")
    print("=" * 80)
    
    for i, test in enumerate(test_cases, 1):
        text = test["text"]
        expected = test["expected"]
        
        found = find_locations_in_text(text)
        found_names = [name for name, _ in found]
        
        status = "✓ PASS" if found_names == expected else "✗ FAIL"
        print(f"\nTest {i}: {status}")
        print(f"  Text: {text}")
        print(f"  Expected: {expected}")
        print(f"  Found: {found_names}")
        
        if found_names != expected:
            print(f"  Details:")
            for name, data in found:
                print(f"    - {name}: {data['country_code']} ({data['lat']}, {data['lng']})")


def test_prefix_splitting():
    """Test prefix splitting"""
    
    test_cases = [
        ("دمشق", "دمشق"),  # No prefix
        ("ودمشق", "دمشق"),  # و prefix
        ("فدمشق", "دمشق"),  # ف prefix
        ("لدمشق", "دمشق"),  # ل prefix
        ("كدمشق", "دمشق"),  # ك prefix
        ("بدمشق", "دمشق"),  # ب prefix
        ("لو", "لو"),  # Too short, don't split
        ("بك", "بك"),  # Too short, don't split
    ]
    
    print("\n" + "=" * 80)
    print("Testing Prefix Splitting")
    print("=" * 80)
    
    for token, expected in test_cases:
        result = split_prefix_if_safe(token)
        status = "✓ PASS" if result == expected else "✗ FAIL"
        print(f"{status}: '{token}' -> '{result}' (expected: '{expected}')")


def test_locations_database():
    """Show available locations"""
    
    print("\n" + "=" * 80)
    print("Available Locations in Database")
    print("=" * 80)
    
    countries = [name for name, data in LOCATIONS_DATABASE.items() if data['type'] == 'country']
    cities = [name for name, data in LOCATIONS_DATABASE.items() if data['type'] == 'city']
    
    print(f"\nCountries ({len(countries)}):")
    for i, country in enumerate(countries, 1):
        data = LOCATIONS_DATABASE[country]
        print(f"  {i:2d}. {country:15s} ({data['country_code']}) - {data['lat']:8.4f}, {data['lng']:8.4f}")
    
    print(f"\nCities ({len(cities)}):")
    for i, city in enumerate(cities, 1):
        data = LOCATIONS_DATABASE[city]
        print(f"  {i:2d}. {city:15s} ({data['country_code']}) - {data['lat']:8.4f}, {data['lng']:8.4f}")


if __name__ == "__main__":
    test_locations_database()
    test_prefix_splitting()
    test_find_locations()
    
    print("\n" + "=" * 80)
    print("All tests completed!")
    print("=" * 80)
