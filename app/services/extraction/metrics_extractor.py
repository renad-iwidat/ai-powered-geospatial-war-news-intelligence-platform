"""
Metrics Extraction Service
Extracts numerical metrics (casualties, weapons, military operations, etc.) from Arabic news text
"""

import re

# ============================================================================
# Arabic Number Words Mapping
# ============================================================================

ARABIC_NUMBERS = {
    # Basic numbers
    'واحد': 1, 'واحدة': 1, 'أحد': 1,
    'اثنين': 2, 'اثنان': 2, 'اثنتين': 2, 'اثنتان': 2, 'ثنتين': 2,
    'ثلاثة': 3, 'ثلاث': 3,
    'أربعة': 4, 'أربع': 4,
    'خمسة': 5, 'خمس': 5,
    'ستة': 6, 'ست': 6,
    'سبعة': 7, 'سبع': 7,
    'ثمانية': 8, 'ثماني': 8, 'ثمان': 8,
    'تسعة': 9, 'تسع': 9,
    'عشرة': 10, 'عشر': 10,
    # Teens
    'أحد عشر': 11, 'احد عشر': 11,
    'اثنا عشر': 12, 'اثني عشر': 12,
    'ثلاثة عشر': 13, 'ثلاث عشرة': 13,
    'أربعة عشر': 14, 'أربع عشرة': 14,
    'خمسة عشر': 15, 'خمس عشرة': 15,
    'ستة عشر': 16, 'ست عشرة': 16,
    'سبعة عشر': 17, 'سبع عشرة': 17,
    'ثمانية عشر': 18, 'ثماني عشرة': 18,
    'تسعة عشر': 19, 'تسع عشرة': 19,
    # Tens
    'عشرون': 20, 'عشرين': 20,
    'ثلاثون': 30, 'ثلاثين': 30,
    'أربعون': 40, 'أربعين': 40,
    'خمسون': 50, 'خمسين': 50,
    'ستون': 60, 'ستين': 60,
    'سبعون': 70, 'سبعين': 70,
    'ثمانون': 80, 'ثمانين': 80,
    'تسعون': 90, 'تسعين': 90,
    # Hundreds
    'مئة': 100, 'مائة': 100,
    'مئتان': 200, 'مئتين': 200, 'مائتان': 200, 'مائتين': 200,
    'ثلاثمئة': 300, 'ثلاثمائة': 300,
    'أربعمئة': 400, 'أربعمائة': 400,
    'خمسمئة': 500, 'خمسمائة': 500,
    'ستمئة': 600, 'ستمائة': 600,
    'سبعمئة': 700, 'سبعمائة': 700,
    'ثمانمئة': 800, 'ثمانمائة': 800,
    'تسعمئة': 900, 'تسعمائة': 900,
    # Thousands
    'ألف': 1000, 'الف': 1000,
    'ألفان': 2000, 'ألفين': 2000, 'الفان': 2000, 'الفين': 2000,
}


# ============================================================================
# Helper Functions
# ============================================================================

def convert_arabic_number_words(text: str) -> str:
    """
    Convert Arabic number words to digits
    Example: "طائرتين مسيرتين" -> "2 طائرة مسيرة"
    
    Handles:
    1. Explicit number words (واحد، اثنين، ثلاثة، etc.)
    2. Dual forms (المثنى) - words ending with ين/ان/تين/تان
    """
    result = text
    
    # First, handle explicit number words
    # Sort by length (longest first) to match compound numbers first
    for word, number in sorted(ARABIC_NUMBERS.items(), key=lambda x: len(x[0]), reverse=True):
        # Replace the word with the number
        result = re.sub(r'\b' + re.escape(word) + r'\b', str(number), result, flags=re.IGNORECASE)
    
    # Handle dual forms (المثنى) - convert "xxxين/xxxان" to "2 xxx"
    # Common dual patterns in war news
    dual_patterns = [
        (r'صاروخين', 'صاروخ'),
        (r'صاروخان', 'صاروخ'),
        (r'طائرتين', 'طائرة'),
        (r'طائرتان', 'طائرة'),
        (r'مسيرتين', 'مسيرة'),
        (r'مسيرتان', 'مسيرة'),
        (r'شخصين', 'شخص'),
        (r'شخصان', 'شخص'),
        (r'قتيلين', 'قتيل'),
        (r'قتيلان', 'قتيل'),
        (r'جريحين', 'جريح'),
        (r'جريحان', 'جريح'),
        (r'مصابين', 'مصاب'),  # This is actually plural, but often used for 2
        (r'جنديين', 'جندي'),
        (r'جنديان', 'جندي'),
        (r'مدنيين', 'مدني'),  # Plural but often for 2
        (r'هدفين', 'هدف'),
        (r'هدفان', 'هدف'),
        (r'موقعين', 'موقع'),
        (r'موقعان', 'موقع'),
    ]
    
    for dual_word, singular in dual_patterns:
        result = re.sub(r'\b' + dual_word + r'\b', f'2 {singular}', result, flags=re.IGNORECASE)
    
    return result

# ============================================================================
# Metric Patterns
# ============================================================================
# Each pattern is a tuple of (metric_type, regex_pattern)
# The regex captures the numerical value for each metric type

PATTERNS = [
    # ========================================================================
    # Missiles & Rockets
    # ========================================================================
    (
        "missiles_launched",
        r"(?:أطلق|أطلقت|اطلق|اطلقت|إطلاق|اطلاق).{0,50}?(\d+)\s*(?:صاروخ|صواريخ)"
    ),
    (
        "missiles_intercepted",
        r"(?:اعترض|اعترضت|أسقط|أسقطت|تم اعتراض|تم إسقاط).{0,50}?(\d+)\s*(?:صاروخ|صواريخ)"
    ),
    (
        "missiles_hit_target",
        r"(?:أصاب|أصابت|وصل|وصلت).{0,50}?(\d+)\s*(?:صاروخ|صواريخ)"
    ),
    
    # ========================================================================
    # Drones & UAVs
    # ========================================================================
    # Pattern 1: verb before number (أطلقت 2 مسيرة)
    (
        "drones_launched",
        r"(?:اطلق|اطلقت|اطلقا|اطلقتا).{0,50}?(\d+)\s*(?:طائرة مسيرة|طائرات مسيرة|مسيرة|مسيرات|درون)"
    ),
    # Pattern 2: number before verb (2 مسيرة أُطلقتا) - simplified
    (
        "drones_launched",
        r"(\d+)\s*(?:طائرة\s*)?(?:مسيرة|مسيرات|درون)"
    ),
    (
        "drones_intercepted",
        r"(?:اعترض|اعترضت|اسقط|اسقطت|تم اعتراض|تم اسقاط).{0,50}?(\d+)\s*(?:طائرة مسيرة|طائرات مسيرة|مسيرة|مسيرات|درون)"
    ),
    
    # ========================================================================
    # Aircraft
    # ========================================================================
    (
        "aircraft_downed",
        r"(?:إسقاط|اسقاط|أسقطت|اسقطت|تم إسقاط).{0,50}?(\d+)\s*(?:طائرة|طائرات|مقاتلة|مقاتلات)"
    ),
    (
        "airstrikes",
        r"(?:غارة|غارات|ضربة جوية|ضربات جوية|قصف جوي).{0,50}?(\d+)"
    ),
    
    # ========================================================================
    # Casualties - Deaths
    # ========================================================================
    (
        "killed",
        r"(?:مقتل|قتل|استشهاد|استشهد|لقي مصرعه|لقوا مصرعهم).{0,30}?(\d+)\s*(?:شخص|أشخاص|شهيد|شهداء|قتيل|قتلى|ضحية|ضحايا)?"
    ),
    (
        "civilians_killed",
        r"(?:مقتل|قتل|استشهاد).{0,30}?(\d+)\s*(?:مدني|مدنيين|مواطن|مواطنين)"
    ),
    (
        "soldiers_killed",
        r"(?:مقتل|قتل|استشهاد).{0,30}?(\d+)\s*(?:جندي|جنود|عسكري|عسكريين)"
    ),
    
    # ========================================================================
    # Casualties - Injuries
    # ========================================================================
    (
        "injured",
        r"(?:اصابة|اصيب|جرح|جرحى|مصاب|مصابين|اسفر عن اصابة).{0,30}?(\d+)\s*(?:شخص|اشخاص|مصاب|مصابين|جريح|جرحى)?"
    ),
    # Simplified pattern: number + person
    (
        "injured",
        r"(\d+)\s*(?:شخص|اشخاص|مصاب|مصابين|جريح|جرحى)"
    ),
    (
        "civilians_injured",
        r"(?:اصابة|اصيب|جرح).{0,30}?(\d+)\s*(?:مدني|مدنيين|مواطن|مواطنين)"
    ),
    
    # ========================================================================
    # Military Operations
    # ========================================================================
    (
        "military_operations",
        r"(?:عملية|عمليات)\s*(?:عسكرية|حربية)?.{0,30}?(\d+)"
    ),
    (
        "airstrikes_count",
        r"(\d+)\s*(?:غارة|غارات|ضربة|ضربات)\s*(?:جوية|جويه)?"
    ),
    (
        "artillery_shells",
        r"(?:أطلق|أطلقت).{0,50}?(\d+)\s*(?:قذيفة|قذائف)\s*(?:مدفعية|مدفعيه)?"
    ),
    
    # ========================================================================
    # Targets & Locations
    # ========================================================================
    (
        "targets_hit",
        r"(?:استهداف|استهدف|استهدفت|قصف|قصفت).{0,50}?(\d+)\s*(?:هدف|أهداف|موقع|مواقع)"
    ),
    (
        "buildings_destroyed",
        r"(?:تدمير|دمر|دمرت|هدم|هدمت).{0,50}?(\d+)\s*(?:مبنى|مباني|منزل|منازل|بناية|بنايات)"
    ),
    
    # ========================================================================
    # Forces & Personnel
    # ========================================================================
    (
        "troops_deployed",
        r"(?:نشر|نشرت|إرسال|أرسل|أرسلت).{0,50}?(\d+)\s*(?:جندي|جنود|عنصر|عناصر|قوة|قوات)"
    ),
    (
        "tanks_deployed",
        r"(?:نشر|نشرت|إرسال).{0,50}?(\d+)\s*(?:دبابة|دبابات|آلية|آليات)"
    ),
    
    # ========================================================================
    # Evacuations & Displacements
    # ========================================================================
    (
        "evacuated",
        r"(?:إجلاء|أجلى|أجليت|إخلاء|أخلى|أخليت).{0,50}?(\d+)\s*(?:شخص|أشخاص|مواطن|مواطنين|عائلة|عائلات)"
    ),
    (
        "displaced",
        r"(?:نزوح|نزح|نزحوا|تهجير|هجر|هجروا).{0,50}?(\d+)\s*(?:شخص|أشخاص|مواطن|مواطنين|عائلة|عائلات)"
    ),
    
    # ========================================================================
    # Numbers with Arabic multipliers (ألف، مليون، إلخ)
    # ========================================================================
    # Pattern 1: Direct "20 ألف"
    (
        "people_count",
        r"(\d+)\s+(?:ألف|الف|مليون|مليار)"
    ),
    # Pattern 2: With context "نحو 20 ألف"
    (
        "people_count",
        r"(?:نحو|حوالي|حوالى|تقريبا|تقريباً)\s+(\d+)\s+(?:ألف|الف|مليون|مليار)"
    ),
]


# ============================================================================
# Extraction Function
# ============================================================================

def extract_metrics(text: str):
    """
    Extract all metrics from the given text
    
    Args:
        text: Arabic text to extract metrics from
        
    Returns:
        List of dictionaries containing:
        - metric_type: Type of metric (e.g., 'killed', 'missiles_launched')
        - value: Numerical value extracted
        - snippet: The sentence where the metric was found
    """
    metrics = []

    if not text:
        return metrics

    try:
        # Normalize text
        text = text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
        
        # Convert Arabic number words to digits
        text = convert_arabic_number_words(text)
        
        # Split text into sentences for better accuracy
        sentences = re.split(r"[\.!\؟\n]", text)

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:  # Skip very short sentences
                continue
                
            # Try each pattern against the sentence
            for metric_type, pattern in PATTERNS:
                try:
                    matches = re.findall(pattern, sentence, re.IGNORECASE)

                    for m in matches:
                        try:
                            value = int(m)
                            
                            # Skip unrealistic values
                            if value <= 0 or value > 100000:
                                continue
                            
                            metrics.append({
                                "metric_type": metric_type,
                                "value": value,
                                "snippet": sentence[:200]  # Limit snippet length
                            })
                            
                        except (ValueError, TypeError):
                            continue
                except Exception:
                    # Skip problematic patterns
                    continue
    except Exception as e:
        # If anything goes wrong, return empty list
        import logging
        logging.error(f"Error extracting metrics: {str(e)}")
        return []

    return metrics
