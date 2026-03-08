#!/usr/bin/env python3
"""
Download and cache CAMeL Tools models
Run this once to download models for offline use
"""

import sys
import os

def download_camel_models():
    """Download CAMeL Tools NER model"""
    print("📥 Downloading CAMeL Tools models...")
    print("=" * 60)
    
    try:
        from camel_tools.ner import NERecognizer
        
        print("⏳ Loading AraBERT NER model (this may take a few minutes)...")
        ner = NERecognizer.pretrained()
        
        print("✅ AraBERT NER model downloaded and cached successfully!")
        print(f"   Location: {os.path.expanduser('~/.camel_tools/data/ner/arabert')}")
        
        # Test it
        print("\n🧪 Testing NER model...")
        test_text = "إيران تقصف إسرائيل من العراق وسوريا"
        result = ner.predict_sentence(test_text.split())
        print(f"   Test text: {test_text}")
        print(f"   Result: {result}")
        
        print("\n✅ All models downloaded and working!")
        return True
        
    except Exception as e:
        print(f"❌ Error downloading models: {str(e)}")
        print("\n💡 Alternative: Use the simple NER instead")
        print("   The system will automatically use simple regex-based NER")
        return False

if __name__ == "__main__":
    success = download_camel_models()
    sys.exit(0 if success else 1)
