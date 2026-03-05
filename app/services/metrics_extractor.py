"""
=============================================================================
War Metrics Extraction Service
=============================================================================
يستخرج مقاييس حربية من النصوص العربية والإنجليزية.
مثل: عدد الصواريخ، الطائرات المسيرة، القتلى، الجرحى، إلخ.

الخطوات:
1. تقسيم النص إلى جمل
2. البحث عن أنماط regex لكل نوع metric
3. التحقق من صحة الأرقام (فلترة منطقية)
4. إرجاع قائمة بـ metrics مع snippet من النص
=============================================================================
"""

import re
from typing import List, Dict, Tuple


# ============================================================================
# Helper Functions
# ============================================================================

def _is_year(n: int) -> bool:
    """التحقق من أن الرقم سنة (1900-2099)"""
    return 1900 <= n <= 2099


def _ok_range(metric_type: str, val: int) -> bool:
    """
    فلترة منطقية للأرقام المستخرجة.
    تتجنب الأرقام الخرافية والسنوات والقيم غير المعقولة.
    """
    # الأرقام السالبة أو صفر غير منطقية
    if val <= 0:
        return False
    
    # السنوات ليست metrics
    if _is_year(val):
        return False
    
    # فلترة حسب نوع الـ metric
    if metric_type in ("killed", "injured") and val > 1_000_000:
        return False
    if metric_type in ("missiles_launched", "drones_launched", "missiles_intercepted") and val > 200_000:
        return False
    if metric_type == "aircraft_down" and val > 10_000:
        return False
    
    return True


def _split_sentences(text: str) -> List[str]:
    """
    تقسيم النص إلى جمل.
    يدعم الفواصل العربية والإنجليزية.
    """
    parts = re.split(r"[\.!\?\؟\n\r]+", text)
    return [p.strip() for p in parts if p and p.strip()]


# ============================================================================
# Arabic Patterns (Context-Based)
# ============================================================================
# أنماط regex للبحث عن metrics في النصوص العربية
# كل pattern يبحث عن كلمات معينة متبوعة برقم

AR_PATTERNS: List[Tuple[str, re.Pattern]] = [
    # إطلاق صواريخ: "أطلقت 50 صاروخ"
    ("missiles_launched", re.compile(r"(?:أطلق|أطلقت|اطلق|اطلقت)\D{0,60}?(\d{1,7})\s*(?:صاروخ|صواريخ)\b")),
    
    # إطلاق طائرات مسيرة: "أطلقت 30 طائرة مسيرة"
    ("drones_launched", re.compile(r"(?:أطلق|أطلقت|اطلق|اطلقت)\D{0,60}?(\d{1,7})\s*(?:طائرة\s*مسيرة|طائرات\s*مسيرة|مسيرة|مسيرات)\b")),
    
    # اعتراض صواريخ: "اعترضت 25 صاروخ"
    ("missiles_intercepted", re.compile(r"(?:اعترضت|اعترض|أسقطت|اسقطت|تم\s*اعتراض)\D{0,60}?(\d{1,7})\s*(?:صاروخ|صواريخ)\b")),
    
    # إسقاط طائرات: "أسقطت 5 طائرات"
    ("aircraft_down", re.compile(r"(?:إسقاط|اسقاط|أسقطت|اسقطت)\D{0,60}?(\d{1,5})\s*(?:طائرة|طائرات)\b")),
    
    # القتلى: "مقتل 100 شخص"
    ("killed", re.compile(r"(?:مقتل|قتل|قُتل|لقي\s*مصرعه|لقي\s*مصرعهم)\D{0,40}?(\d{1,7})\b")),
    
    # الجرحى: "إصابة 200 جريح"
    ("injured", re.compile(r"(?:إصابة|أُصيب|اصيب|جُرح|جرح)\D{0,40}?(\d{1,7})\b")),
]


# ============================================================================
# English Fallback Patterns
# ============================================================================
# أنماط للبحث في النصوص الإنجليزية (في حالة عدم وجود ترجمة عربية)

EN_PATTERNS: List[Tuple[str, re.Pattern]] = [
    ("missiles_launched", re.compile(r"(?:launched|fired)\D{0,40}?(\d{1,7})\s*(?:missile|missiles)\b", re.I)),
    ("drones_launched", re.compile(r"(?:launched|deployed|sent)\D{0,40}?(\d{1,7})\s*(?:drone|drones|UAVs?)\b", re.I)),
    ("missiles_intercepted", re.compile(r"(?:intercepted|shot\s*down)\D{0,40}?(\d{1,7})\s*(?:missile|missiles)\b", re.I)),
    ("aircraft_down", re.compile(r"(?:shot\s*down|downed)\D{0,40}?(\d{1,5})\s*(?:aircraft|plane|jet|jets)\b", re.I)),
    ("killed", re.compile(r"(\d{1,7})\s*(?:killed|dead)\b", re.I)),
    ("injured", re.compile(r"(\d{1,7})\s*(?:injured|wounded)\b", re.I)),
]


# ============================================================================
# Main Extraction Function
# ============================================================================

def extract_war_metrics(text: str, prefer_lang: str = "ar") -> List[Dict]:
    """
    استخراج مقاييس حربية من النص.
    
    Args:
        text: النص المراد البحث فيه
        prefer_lang: اللغة المفضلة للبحث ('ar' أو 'en')
                    إذا لم يجد نتائج باللغة المفضلة، يحاول اللغة الأخرى
    
    Returns:
        قائمة بـ dictionaries تحتوي على:
        - metric_type: نوع الـ metric (missiles_launched, killed, إلخ)
        - value: القيمة الرقمية
        - snippet: أول 200 حرف من الجملة التي تم استخراج الـ metric منها
    """
    if not text or not text.strip():
        return []

    sentences = _split_sentences(text)
    results: List[Dict] = []

    def run(patterns: List[Tuple[str, re.Pattern]]):
        """تطبيق مجموعة أنماط على الجمل"""
        nonlocal results
        for sent in sentences:
            for metric_type, rx in patterns:
                for m in rx.findall(sent):
                    try:
                        val = int(m)
                    except:
                        continue
                    
                    # فلترة الأرقام غير المنطقية
                    if not _ok_range(metric_type, val):
                        continue
                    
                    results.append({
                        "metric_type": metric_type,
                        "value": val,
                        "snippet": sent[:200]  # أول 200 حرف من الجملة
                    })

    # البحث باللغة المفضلة أولاً
    if prefer_lang == "en":
        run(EN_PATTERNS)
        if not results:
            run(AR_PATTERNS)
    else:
        run(AR_PATTERNS)
        if not results:
            run(EN_PATTERNS)

    return results
