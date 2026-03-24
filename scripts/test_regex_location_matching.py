#!/usr/bin/env python3
"""
Test Regex Location Matching
اختبار البحث عن المواقع باستخدام Regex
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.geo.location_processor import find_locations_in_text


def test_regex_matching():
    """اختبار البحث عن المواقع باستخدام Regex"""
    
    test_cases = [
        {
            "text": "حدث انفجار في بيروت وأثر على دمشق",
            "expected": ["بيروت", "دمشق"],
            "description": "أسماء مدن بسيطة"
        },
        {
            "text": "الأخبار من الرياض، والقاهرة تشير إلى تطورات جديدة",
            "expected": ["الرياض", "القاهرة"],
            "description": "أسماء مع فاصلات"
        },
        {
            "text": "وبغداد: وطهران يناقشان الأوضاع",
            "expected": ["بغداد", "طهران"],
            "description": "أسماء مع حروف جر ونقطتان"
        },
        {
            "text": "لبنان وسوريا والعراق يعقدون اجتماعات",
            "expected": ["لبنان", "سوريا", "العراق"],
            "description": "أسماء مع حروف جر"
        },
        {
            "text": "في إسطنبول. وأنقرة تم توقيع اتفاقية",
            "expected": ["إسطنبول", "أنقرة"],
            "description": "أسماء مع نقاط"
        },
        {
            "text": "بيروت، دمشق: بغداد. طهران",
            "expected": ["بيروت", "دمشق", "بغداد", "طهران"],
            "description": "أسماء مع رموز متعددة"
        },
        {
            "text": "ولبنان، والعراق: وسوريا.",
            "expected": ["لبنان", "العراق", "سوريا"],
            "description": "أسماء مع حروف جر ورموز"
        },
        {
            "text": "غزة، نابلس، رام الله في فلسطين",
            "expected": ["غزة", "فلسطين"],
            "description": "مواقع فلسطينية"
        },
        {
            "text": "القدس: عاصمة فلسطين التاريخية",
            "expected": ["القدس", "فلسطين"],
            "description": "مواقع مع نقطتان"
        },
        {
            "text": "من بيروت إلى دمشق ومن بغداد إلى طهران",
            "expected": ["بيروت", "دمشق", "بغداد", "طهران"],
            "description": "أسماء متكررة (يجب إزالة التكرار)"
        },
    ]
    
    print("=" * 80)
    print("اختبار البحث عن المواقع باستخدام Regex")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        text = test["text"]
        expected = test["expected"]
        description = test["description"]
        
        found = find_locations_in_text(text)
        found_names = [name for name, _ in found]
        
        # المقارنة باستخدام set لتجاهل الترتيب
        status = "✓ PASS" if set(found_names) == set(expected) else "✗ FAIL"
        
        if set(found_names) == set(expected):
            passed += 1
        else:
            failed += 1
        
        print(f"\nTest {i}: {status}")
        print(f"  الوصف: {description}")
        print(f"  النص: {text}")
        print(f"  المتوقع: {expected}")
        print(f"  الفعلي: {found_names}")
        
        if found_names != expected:
            print(f"  الفرق:")
            missing = set(expected) - set(found_names)
            extra = set(found_names) - set(expected)
            if missing:
                print(f"    - ناقص: {missing}")
            if extra:
                print(f"    - إضافي: {extra}")
    
    print("\n" + "=" * 80)
    print("النتائج")
    print("=" * 80)
    print(f"نجح: {passed}/{len(test_cases)}")
    print(f"فشل: {failed}/{len(test_cases)}")
    print(f"النسبة المئوية: {(passed/len(test_cases)*100):.1f}%")
    print("=" * 80 + "\n")


def test_edge_cases():
    """اختبار الحالات الحدية"""
    
    print("=" * 80)
    print("اختبار الحالات الحدية")
    print("=" * 80)
    
    edge_cases = [
        {
            "text": "بيروت",
            "expected": ["بيروت"],
            "description": "كلمة واحدة"
        },
        {
            "text": "بيروت،",
            "expected": ["بيروت"],
            "description": "كلمة مع فاصلة"
        },
        {
            "text": "ولبنان",
            "expected": ["لبنان"],
            "description": "كلمة مع حرف جر"
        },
        {
            "text": "ولبنان،",
            "expected": ["لبنان"],
            "description": "كلمة مع حرف جر وفاصلة"
        },
        {
            "text": "والعراق:",
            "expected": ["العراق"],
            "description": "كلمة مع حرف جر ونقطتان"
        },
        {
            "text": "بيروت بيروت بيروت",
            "expected": ["بيروت"],
            "description": "كلمة مكررة (يجب إزالة التكرار)"
        },
        {
            "text": "لا توجد مواقع هنا",
            "expected": [],
            "description": "نص بدون مواقع"
        },
        {
            "text": "",
            "expected": [],
            "description": "نص فارغ"
        },
    ]
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(edge_cases, 1):
        text = test["text"]
        expected = test["expected"]
        description = test["description"]
        
        found = find_locations_in_text(text)
        found_names = [name for name, _ in found]
        
        status = "✓ PASS" if found_names == expected else "✗ FAIL"
        
        if found_names == expected:
            passed += 1
        else:
            failed += 1
        
        print(f"\nEdge Case {i}: {status}")
        print(f"  الوصف: {description}")
        print(f"  النص: '{text}'")
        print(f"  المتوقع: {expected}")
        print(f"  الفعلي: {found_names}")
    
    print("\n" + "=" * 80)
    print("نتائج الحالات الحدية")
    print("=" * 80)
    print(f"نجح: {passed}/{len(edge_cases)}")
    print(f"فشل: {failed}/{len(edge_cases)}")
    print(f"النسبة المئوية: {(passed/len(edge_cases)*100):.1f}%")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    test_regex_matching()
    test_edge_cases()
