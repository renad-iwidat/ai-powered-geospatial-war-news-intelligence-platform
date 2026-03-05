"""
Test extraction on a single text
"""
import sys
sys.path.insert(0, '.')

from app.services.extraction.metrics_extractor import extract_metrics

# Test text with clear metrics
text = """
أكدت وزارة الخارجية الأذربيجانية صباح اليوم (الخميس) أن طائرتين مسيرتين 
أُطلقتا من أراضي إيران استهدفتا مطارًا مدنيًا وعسكريًا بالقرب من مدرسة 
في جيب ناخشيفان بأذربيجان، مما أسفر عن إصابة شخصين.
"""

print("Testing extraction on:")
print(text)
print("\n" + "=" * 80)

metrics = extract_metrics(text)

if metrics:
    print(f"✅ Found {len(metrics)} metrics:")
    for m in metrics:
        print(f"  - {m['metric_type']}: {m['value']}")
        print(f"    Snippet: {m['snippet'][:100]}")
else:
    print("❌ No metrics found")
