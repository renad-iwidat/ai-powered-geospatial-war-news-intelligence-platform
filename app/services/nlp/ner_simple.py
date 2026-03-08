"""
Simple Arabic Place Name Extraction
Alternative to CAMeL Tools NER - uses regex and known place names
"""

import re
from typing import List

# ============================================================================
# Known Places Dictionary
# ============================================================================
# Maps place names to their country codes
KNOWN_PLACES = {
    # Middle East - Countries
    'إيران': 'IR',
    'ايران': 'IR',
    'العراق': 'IQ',
    'العراقي': 'IQ',
    'سوريا': 'SY',
    'السوري': 'SY',
    'السورية': 'SY',
    'إسرائيل': 'IL',
    'اسرائيل': 'IL',
    'الإسرائيلي': 'IL',
    'فلسطين': 'PS',
    'الفلسطيني': 'PS',
    'لبنان': 'LB',
    'اللبناني': 'LB',
    'اليمن': 'YE',
    'اليمني': 'YE',
    'السعودية': 'SA',
    'السعودي': 'SA',
    'الإمارات': 'AE',
    'الإمارة': 'AE',
    'الإماراتي': 'AE',
    'الكويت': 'KW',
    'الكويتي': 'KW',
    'قطر': 'QA',
    'القطري': 'QA',
    'البحرين': 'BH',
    'البحريني': 'BH',
    'عمان': 'OM',
    'العماني': 'OM',
    'الأردن': 'JO',
    'الأردني': 'JO',
    'مصر': 'EG',
    'المصري': 'EG',
    'تركيا': 'TR',
    'التركي': 'TR',
    'أفغانستان': 'AF',
    'باكستان': 'PK',
    'الهند': 'IN',
    'الهندي': 'IN',
    'روسيا': 'RU',
    'الروسي': 'RU',
    'أمريكا': 'US',
    'الأمريكي': 'US',
    'أوروبا': 'EU',
    'الأوروبي': 'EU',
    'الصين': 'CN',
    'الصيني': 'CN',
    'اليابان': 'JP',
    'الياباني': 'JP',
    'كوريا': 'KR',
    'الكوري': 'KR',
    
    # Major Cities
    'دمشق': 'SY',
    'بغداد': 'IQ',
    'طهران': 'IR',
    'تهران': 'IR',
    'القاهرة': 'EG',
    'الرياض': 'SA',
    'الدوحة': 'QA',
    'أبو ظبي': 'AE',
    'دبي': 'AE',
    'عمّان': 'JO',
    'بيروت': 'LB',
    'صنعاء': 'YE',
    'عدن': 'YE',
    'الكويت': 'KW',
    'المنامة': 'BH',
    'مسقط': 'OM',
    'أنقرة': 'TR',
    'اسطنبول': 'TR',
    'موسكو': 'RU',
    'واشنطن': 'US',
    'نيويورك': 'US',
    'لندن': 'GB',
    'باريس': 'FR',
    'برلين': 'DE',
    'بكين': 'CN',
    'طوكيو': 'JP',
    'دلهي': 'IN',
    'إسلام آباد': 'PK',
    'كابل': 'AF',
    'القدس': 'PS',
    'رام الله': 'PS',
    'غزة': 'PS',
    'تل أبيب': 'IL',
    'الإسكندرية': 'EG',
    'حلب': 'SY',
    'حمص': 'SY',
    'اللاذقية': 'SY',
    'الموصل': 'IQ',
    'البصرة': 'IQ',
    'كربلاء': 'IQ',
    'النجف': 'IQ',
    'أربيل': 'IQ',
    'السليمانية': 'IQ',
    'تكريت': 'IQ',
    'الفلوجة': 'IQ',
    'الرمادي': 'IQ',
    'الأنبار': 'IQ',
    'ديالى': 'IQ',
    'واسط': 'IQ',
    'ميسان': 'IQ',
    'ذي قار': 'IQ',
    'المثنى': 'IQ',
    'بابل': 'IQ',
    'الحلة': 'IQ',
    'كيش': 'IR',
    'قم': 'IR',
    'مشهد': 'IR',
    'أصفهان': 'IR',
    'شيراز': 'IR',
    'تبريز': 'IR',
    'رشت': 'IR',
    'بندر عباس': 'IR',
    'أهواز': 'IR',
    'خرمشهر': 'IR',
    'الأحواز': 'IR',
    'خوزستان': 'IR',
    'فارس': 'IR',
    'هرمزگان': 'IR',
    'سيستان': 'IR',
    'بلوچستان': 'IR',
    'كرمان': 'IR',
    'يزد': 'IR',
    'همدان': 'IR',
    'كرمانشاه': 'IR',
    'إيلام': 'IR',
    'لرستان': 'IR',
    'مركزی': 'IR',
    'قزوین': 'IR',
    'البحر الأحمر': 'YE',
    'خليج عدن': 'YE',
    'مضيق باب المندب': 'YE',
    'الخليج': 'UNKNOWN',
    'الخليج العربي': 'UNKNOWN',
    'خليج فارس': 'IR',
    'البحر المتوسط': 'UNKNOWN',
    'البحر الأسود': 'UNKNOWN',
    'بحر قزوين': 'UNKNOWN',
    'بحر الشرقية': 'UNKNOWN',
    'المحيط الهندي': 'UNKNOWN',
    'المحيط الأطلسي': 'UNKNOWN',
    'مضيق هرمز': 'UNKNOWN',
    'مضيق تيران': 'UNKNOWN',
    'مضيق جبل طارق': 'UNKNOWN',
    'قناة السويس': 'EG',
    'سيناء': 'EG',
    'النقب': 'IL',
    'الجولان': 'SY',
    'الضفة الغربية': 'PS',
    'الشرقية': 'PS',
    'الجنوب': 'LB',
    'البقاع': 'LB',
    'الشمال': 'LB',
    'جبل لبنان': 'LB',
    'الساحل': 'LB',
    'الحدود': 'UNKNOWN',
    'المنطقة الحدودية': 'UNKNOWN',
    'المنطقة الخضراء': 'IQ',
    'المنطقة الحمراء': 'UNKNOWN',
    'المنطقة الآمنة': 'UNKNOWN',
    'المنطقة العسكرية': 'UNKNOWN',
    'القاعدة العسكرية': 'UNKNOWN',
    'المطار': 'UNKNOWN',
    'الميناء': 'UNKNOWN',
    'الحدود السورية': 'SY',
    'الحدود العراقية': 'IQ',
    'الحدود الإيرانية': 'IR',
    'الحدود الإسرائيلية': 'IL',
    'الحدود اللبنانية': 'LB',
    'الحدود الأردنية': 'JO',
    'الحدود السعودية': 'SA',
    'الحدود الكويتية': 'KW',
    'الحدود التركية': 'TR',
    'الحدود الأفغانية': 'AF',
    'الحدود الباكستانية': 'PK',
}

# ============================================================================
# Helper Functions
# ============================================================================

def normalize_ar(s: str) -> str:
    """Normalize Arabic text"""
    s = (s or "").strip()
    
    # Remove diacritics
    s = re.sub(r"[\u064B-\u0652]", "", s)
    
    # Normalize alef
    s = s.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    
    # Normalize taa marbuta
    s = s.replace("ة", "ه")
    
    # Remove extra spaces
    s = re.sub(r"\s+", " ", s)
    
    return s


# ============================================================================
# Main Extraction Function
# ============================================================================

def extract_places_simple(text: str) -> List[str]:
    """
    Extract place names from Arabic text using simple regex + known places
    
    Args:
        text: Arabic text to extract places from
    
    Returns:
        List of unique place names
    """
    if not text or len(text.strip()) < 3:
        return []
    
    # Normalize text
    text = normalize_ar(text)
    
    places = []
    seen = set()
    
    # Search for known places in text
    for place_name in KNOWN_PLACES.keys():
        # Use word boundaries to match whole words
        pattern = r'\b' + re.escape(place_name) + r'\b'
        
        if re.search(pattern, text, re.IGNORECASE):
            normalized = normalize_ar(place_name)
            if normalized not in seen and len(normalized) >= 2:
                places.append(normalized)
                seen.add(normalized)
    
    # Also search for places with Arabic prefixes (ب، ل، ف، و، ك)
    # This catches cases like "لايران" → "ايران", "بسوريا" → "سوريا"
    ar_prefixes = ['ب', 'ل', 'ف', 'و', 'ك']
    
    for prefix in ar_prefixes:
        for place_name in KNOWN_PLACES.keys():
            # Try with prefix
            prefixed_pattern = r'\b' + re.escape(prefix + place_name) + r'\b'
            
            if re.search(prefixed_pattern, text, re.IGNORECASE):
                normalized = normalize_ar(place_name)
                if normalized not in seen and len(normalized) >= 2:
                    places.append(normalized)
                    seen.add(normalized)
    
    return places
