"""
Arabic Named Entity Recognition using CAMeL Tools
High-quality NER for Arabic text
"""

import re
from typing import List
from camel_tools.ner import NERecognizer


# ============================================================================
# Initialize CAMeL NER
# ============================================================================
_ner = None

def get_ner():
    """Get or initialize CAMeL NER"""
    global _ner
    if _ner is None:
        _ner = NERecognizer.pretrained()
    return _ner


# ============================================================================
# Helper Functions
# ============================================================================

def normalize_ar(s: str) -> str:
    """
    Normalize Arabic text
    
    Steps:
    1. Remove diacritics
    2. Normalize alef variants
    3. Normalize taa marbuta
    4. Remove extra spaces
    """
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

def extract_places_ner(text: str) -> List[str]:
    """
    Extract place names from Arabic text using CAMeL Tools NER
    
    Extracts entities of type:
    - LOC: Geographic locations
    - GPE: Geopolitical entities (countries, cities)
    
    Args:
        text: Arabic text to extract places from
    
    Returns:
        List of unique place names (normalized)
    """
    if not text or len(text.strip()) < 3:
        return []
    
    # Get NER
    ner = get_ner()
    
    # Split into sentences (CAMeL works better with sentences)
    sentences = re.split(r'[\.!\؟\n]+', text)
    
    places = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) < 3:
            continue
        
        # Run NER
        try:
            labels = ner.predict_sentence(sentence.split())
            
            # Extract LOC and GPE entities
            current_entity = []
            current_type = None
            
            for word, label in zip(sentence.split(), labels):
                if label.startswith('B-'):
                    # Beginning of entity
                    if current_entity and current_type in ('LOC', 'GPE'):
                        entity_text = ' '.join(current_entity)
                        normalized = normalize_ar(entity_text)
                        if len(normalized) >= 2:
                            places.append(normalized)
                    
                    current_entity = [word]
                    current_type = label[2:]  # Remove 'B-'
                    
                elif label.startswith('I-') and current_entity:
                    # Inside entity
                    current_entity.append(word)
                    
                else:
                    # Outside entity
                    if current_entity and current_type in ('LOC', 'GPE'):
                        entity_text = ' '.join(current_entity)
                        normalized = normalize_ar(entity_text)
                        if len(normalized) >= 2:
                            places.append(normalized)
                    
                    current_entity = []
                    current_type = None
            
            # Don't forget last entity
            if current_entity and current_type in ('LOC', 'GPE'):
                entity_text = ' '.join(current_entity)
                normalized = normalize_ar(entity_text)
                if len(normalized) >= 2:
                    places.append(normalized)
                    
        except Exception:
            # Skip problematic sentences
            continue
    
    # Remove duplicates while preserving order
    seen = set()
    unique_places = []
    for place in places:
        if place not in seen:
            seen.add(place)
            unique_places.append(place)
    
    return unique_places
