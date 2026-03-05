"""
Test full extraction flow
"""
import sys
import re
sys.path.insert(0, '.')

text_original = """
أكدت وزارة الخارجية الأذربيجانية صباح اليوم (الخميس) أن طائرتين مسيرتين 
أُطلقتا من أراضي إيران استهدفتا مطارًا مدنيًا وعسكريًا بالقرب من مدرسة 
في جيب ناخشيفان بأذربيجان، مما أسفر عن إصابة شخصين.
"""

print("Step 1: Original text")
print(text_original)
print("\n" + "=" * 80)

# Step 2: Normalize
text_normalized = text_original.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
print("Step 2: After normalization")
print(text_normalized)
print("\n" + "=" * 80)

# Step 3: Convert numbers
from app.services.extraction.metrics_extractor import convert_arabic_number_words
text_converted = convert_arabic_number_words(text_normalized)
print("Step 3: After number conversion")
print(text_converted)
print("\n" + "=" * 80)

# Step 4: Test pattern
pattern = r"(\d+)\s*(?:طائرة مسيرة|طائرات مسيرة|مسيرة|مسيرات|درون).{0,50}?(?:اطلق|اطلقت|اطلقا|اطلقتا)"
matches = re.findall(pattern, text_converted, re.IGNORECASE)
print(f"Step 4: Pattern matches: {matches}")
