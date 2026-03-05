"""
Test simpler pattern
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

# Simpler: just find number + مسيرة in context of launching
sentences = text.split('.')
for sent in sentences:
    if 'مسيرة' in sent and any(word in sent for word in ['طلق', 'طلقت', 'طلقا', 'طلقتا']):
        print(f"Found relevant sentence: {sent[:100]}")
        # Extract numbers before مسيرة
        pattern = r'(\d+)\s*(?:طائرة\s*)?(?:مسيرة|مسيرات)'
        matches = re.findall(pattern, sent)
        print(f"Numbers found: {matches}")
