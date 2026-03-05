"""
Test regex pattern manually
"""
import re

text = """
أكدت وزارة الخارجية الأذربيجانية صباح اليوم (الخميس) أن 2 طائرة 2 مسيرة 
أُطلقتا من أراضي إيران استهدفتا مطارًا مدنيًا وعسكريًا بالقرب من مدرسة 
في جيب ناخشيفان بأذربيجان، مما أسفر عن إصابة 2 شخص.
"""

print("Text:")
print(text)
print("\n" + "=" * 80)

# Test drones pattern
pattern1 = r"(?:أطلق|أطلقت|أُطلق|أُطلقت|اطلق|اطلقت|إطلاق|أُطلقا|أُطلقتا).{0,50}?(\d+)\s*(?:طائرة مسيرة|طائرات مسيرة|مسيرة|مسيرات|درون)"
matches1 = re.findall(pattern1, text, re.IGNORECASE)
print(f"Drones pattern matches: {matches1}")

# Test injury pattern
pattern2 = r"(?:إصابة|أصيب|أُصيب|جرح|جُرح|جرحى|مصاب|مصابين|أسفر عن إصابة).{0,30}?(\d+)\s*(?:شخص|أشخاص|مصاب|مصابين|جريح|جرحى)?"
matches2 = re.findall(pattern2, text, re.IGNORECASE)
print(f"Injury pattern matches: {matches2}")

# Try simpler patterns
pattern3 = r"(\d+)\s*(?:طائرة|مسيرة)"
matches3 = re.findall(pattern3, text)
print(f"Simple drone pattern: {matches3}")

pattern4 = r"(\d+)\s*شخص"
matches4 = re.findall(pattern4, text)
print(f"Simple person pattern: {matches4}")
