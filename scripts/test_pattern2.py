"""
Test pattern with actual normalized text
"""
import re

text = """
اكدت وزارة الخارجية الاذربيجانية صباح اليوم (الخميس) ان 2 طائرة 2 مسيرة 
اُطلقتا من اراضي ايران استهدفتا مطارًا مدنيًا وعسكريًا بالقرب من مدرسة 
في جيب ناخشيفان باذربيجان، مما اسفر عن اصابة 2 شخص.
"""

print("Text:")
print(text)
print("\n" + "=" * 80)

# Test with flexible pattern (any character for hamza)
pattern1 = r"(\d+)\s*(?:طائرة|مسيرة).{0,50}?(?:.طلق|.طلقت|.طلقا|.طلقتا)"
matches1 = re.findall(pattern1, text, re.IGNORECASE)
print(f"Flexible pattern matches: {matches1}")

# Test injury pattern
pattern2 = r"(?:.صابة|.صيب|.سفر عن .صابة).{0,30}?(\d+)\s*شخص"
matches2 = re.findall(pattern2, text, re.IGNORECASE)
print(f"Injury pattern matches: {matches2}")
