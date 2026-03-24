#!/usr/bin/env python3
"""
Test Location Uniqueness
اختبار أن المواقع المرجعة unique (بدون تكرار)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.geo.location_processor import find_locations_in_text


def test_uniqueness():
    """اختبار أن المواقع المرجعة unique"""
    
    test_cases = [
        {
            "text": "لبنان لبنان لبنان",
            "expected_count": 1,
            "description": "نفس الموقع مكرر 3 مرات"
        },
        {
            "text": "بيروت بيروت دمشق دمشق",
            "expected_count": 2,
            "description": "موقعين مكررين"
        },
        {
            "text": "ولبنان والعراق ولبنان والعراق",
            "expected_count": 2,
            "description": "موقعين مع حروف جر مكررين"
        },
        {
            "text": "بيروت، بيروت: بيروت.",
            "expected_count": 1,
            "description": "نفس الموقع مع رموز مختلفة"
        },
        {
            "text": "من بيروت إلى دمشق ومن بغداد إلى طهران ومن بيروت إلى دمشق",
            "expected_count": 4,
            "description": "4 مواقع مع تكرار"
        },
    ]
    
    print("=" * 80)
    print("اختبار Uniqueness - المواقع المرجعة بدون تكرار")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        text = test["text"]
        expected_count = test["expected_count"]
        description = test["description"]
        
        found = find_locations_in_text(text)
        found_names = [name for name, _ in found]
        actual_count = len(found_names)
        
        # التحقق من عدم التكرار
        is_unique = len(found_names) == len(set(found_names))
        
        status = "✓ PASS" if actual_count == expected_count and is_unique else "✗ FAIL"
        
        if actual_count == expected_count and is_unique:
            passed += 1
        else:
            failed += 1
        
        print(f"\nTest {i}: {status}")
        print(f"  الوصف: {description}")
        print(f"  النص: {text}")
        print(f"  المتوقع: {expected_count} موقع")
        print(f"  الفعلي: {actual_count} موقع")
        print(f"  المواقع: {found_names}")
        print(f"  Unique: {'✓ نعم' if is_unique else '✗ لا'}")
        
        if actual_count != expected_count:
            print(f"  ✗ خطأ: عدد المواقع غير صحيح")
        if not is_unique:
            print(f"  ✗ خطأ: توجد مواقع مكررة")
    
    print("\n" + "=" * 80)
    print("النتائج")
    print("=" * 80)
    print(f"نجح: {passed}/{len(test_cases)}")
    print(f"فشل: {failed}/{len(test_cases)}")
    print(f"النسبة المئوية: {(passed/len(test_cases)*100):.1f}%")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    test_uniqueness()
