"""
Metrics Extraction Service
Extracts numerical metrics (casualties, weapons, etc.) from Arabic news text
"""

import re

# ============================================================================
# Metric Patterns
# ============================================================================
# Each pattern is a tuple of (metric_type, regex_pattern)
# The regex captures the numerical value for each metric type

PATTERNS = [
    # Missiles launched
    (
        "missiles_launched",
        r"(?:أطلق|أطلقت|اطلق|اطلقت)\D{0,40}?(\d+)\s*(?:صاروخ|صواريخ)"
    ),

    # Drones/UAVs launched
    (
        "drones_launched",
        r"(?:أطلق|أطلقت|اطلق|اطلقت)\D{0,40}?(\d+)\s*(?:طائرة مسيرة|طائرات مسيرة|مسيرة|مسيرات)"
    ),

    # Missiles intercepted
    (
        "missiles_intercepted",
        r"(?:اعترض|أسقط|تم اعتراض)\D{0,40}?(\d+)\s*(?:صاروخ|صواريخ)"
    ),

    # Killed/Deaths
    (
        "killed",
        r"(?:مقتل|قتل|لقي\sمصرعه)\D{0,10}?(\d+)"
    ),

    # Injured/Wounded
    (
        "injured",
        r"(?:إصابة|أصيب|جرح)\D{0,10}?(\d+)"
    ),

    # Aircraft downed
    (
        "aircraft_down",
        r"(?:إسقاط|اسقاط|أسقطت|اسقطت)\D{0,40}?(\d+)\s*(?:طائرة|طائرات)"
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

    # Split text into sentences for better accuracy
    sentences = re.split(r"[\.!\؟\n]", text)

    for sentence in sentences:
        # Try each pattern against the sentence
        for metric_type, pattern in PATTERNS:
            matches = re.findall(pattern, sentence)

            for m in matches:
                try:
                    value = int(m)
                except (ValueError, TypeError):
                    continue

                metrics.append({
                    "metric_type": metric_type,
                    "value": value,
                    "snippet": sentence.strip()
                })

    return metrics
