"""
Debug number conversion
"""
import sys
sys.path.insert(0, '.')

from app.services.extraction.metrics_extractor import convert_arabic_number_words

text = """
أكدت وزارة الخارجية الأذربيجانية صباح اليوم (الخميس) أن طائرتين مسيرتين 
أُطلقتا من أراضي إيران استهدفتا مطارًا مدنيًا وعسكريًا بالقرب من مدرسة 
في جيب ناخشيفان بأذربيجان، مما أسفر عن إصابة شخصين.
"""

print("Original text:")
print(text)
print("\n" + "=" * 80)

converted = convert_arabic_number_words(text)
print("After conversion:")
print(converted)
