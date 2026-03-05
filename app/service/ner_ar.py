import re
import stanza
from typing import List

# تحميل الـ pipeline مرة واحدة
nlp = stanza.Pipeline(
    lang="ar",
    processors="tokenize,ner",
    tokenize_no_ssplit=True
)

def normalize_ar(s: str) -> str:
    s = (s or "").strip()
    s = re.sub(r"[\u064B-\u0652]", "", s)  # إزالة التشكيل
    s = s.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    s = s.replace("ة", "ه")
    s = re.sub(r"\s+", " ", s)
    return s

def extract_places_ner(text: str) -> List[str]:
    """
    الهدف: استخراج أسماء أماكن من النص العربي.
    Stanza يعطينا كيانات NER. اللي بنهمنا: LOC/GPE.
    """
    if not text or len(text.strip()) < 3:
        return []

    doc = nlp(text)
    places = []

    for ent in doc.ents:
        label = ent.type.upper()
        if label in ("LOC", "GPE"):
            val = normalize_ar(ent.text)
            if len(val) >= 2:
                places.append(val)

    # unique
    out = []
    seen = set()
    for p in places:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out