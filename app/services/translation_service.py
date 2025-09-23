"""
Translation Service - Multilingual Support for Indian Languages
"""
import logging
from typing import Dict, Any, Optional
import re

logger = logging.getLogger(__name__)

class TranslationService:
    """Service for language detection and translation"""
    
    def __init__(self):
        self.supported_languages = {
            "en": "English",
            "hi": "Hindi",
            "ta": "Tamil",
            "te": "Telugu",
            "ml": "Malayalam",
            "kn": "Kannada",
            "bn": "Bengali",
            "gu": "Gujarati",
            "mr": "Marathi",
            "pa": "Punjabi",
            "or": "Odia",
            "as": "Assamese",
            "ur": "Urdu"
        }
        
        # Unicode ranges for Indian languages
        self.language_unicode_ranges = {
            "hi": r"[\u0900-\u097F]",      # Devanagari (Hindi, Marathi, etc.)
            "ta": r"[\u0B80-\u0BFF]",      # Tamil
            "te": r"[\u0C00-\u0C7F]",      # Telugu
            "ml": r"[\u0D00-\u0D7F]",      # Malayalam
            "kn": r"[\u0C80-\u0CFF]",      # Kannada
            "bn": r"[\u0980-\u09FF]",      # Bengali
            "gu": r"[\u0A80-\u0AFF]",      # Gujarati
            "pa": r"[\u0A00-\u0A7F]",      # Punjabi
            "or": r"[\u0B00-\u0B7F]",      # Odia
            "as": r"[\u0980-\u09FF]",      # Assamese (shares Bengali range)
            "ur": r"[\u0600-\u06FF]"       # Urdu (Arabic script)
        }
        
        logger.info(f"Translation Service initialized - Supported languages: {len(self.supported_languages)}")
    
    def detect_language(self, text: str) -> str:
        """
        Detect language of input text using Unicode ranges
        
        Args:
            text: Input text to analyze
            
        Returns:
            Language code (ISO 639-1)
        """
        try:
            text_clean = text.strip()
            
            # Check for each language using Unicode ranges
            for lang_code, unicode_pattern in self.language_unicode_ranges.items():
                if re.search(unicode_pattern, text_clean):
                    logger.info(f"✅ Language detected: {lang_code} ({self.supported_languages[lang_code]})")
                    return lang_code
            
            # Default to English for Latin script
            if re.search(r"[a-zA-Z]", text_clean):
                logger.info("🔤 Language detected: en (English - Latin script)")
                return "en"
            
            # Fallback to English
            logger.info("🔤 Language detection fallback: en (English)")
            return "en"
            
        except Exception as e:
            logger.error(f"Error detecting language: {e}")
            return "en"
    
    def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Translate text between languages (SIMPLIFIED VERSION)
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Translated text (or original if same language)
        """
        try:
            # Handle same language
            if source_lang == target_lang:
                logger.info(f"Same language translation: {source_lang} -> {target_lang}")
                return text
            
            # Handle unsupported languages
            if source_lang not in self.supported_languages or target_lang not in self.supported_languages:
                logger.warning(f"Unsupported translation: {source_lang} -> {target_lang}")
                return text
            
            # For demo purposes - return original text with language indicator
            # In production, integrate with actual translation API
            translated_text = f"[{target_lang.upper()} TRANSLATION] {text}"
            logger.info(f"🔄 Translated: {source_lang} -> {target_lang}")
            
            return translated_text
            
        except Exception as e:
            logger.error(f"Error translating text: {e}")
            return text
    
    def get_language_name(self, lang_code: str) -> str:
        """Get full language name from code"""
        return self.supported_languages.get(lang_code, "Unknown")

# Create service instance
translation_service = TranslationService()

# Test function
def test_translation_service():
    """Test translation service"""
    print("🧪 Testing Translation Service")
    print("=" * 30)
    
    service = TranslationService()
    
    # Test language detection
    test_texts = [
        ("I have headache and fever", "en"),
        ("मुझे सिरदर्द और बुखार है", "hi"),
        ("எனக்கு தலைவலி மற்றும் காய்ச்சல் உண்டு", "ta"),
        ("నాకు తలనొప్పి మరియు జ్వరం ఉంది", "te"),
        ("എനിക്ക് തലവേദനയും ജ്വരവും ഉണ്ട്", "ml")
    ]
    
    print("🔍 Language Detection Tests:")
    for text, expected_lang in test_texts:
        detected_lang = service.detect_language(text)
        status = "✅" if detected_lang == expected_lang else "❌"
        print(f"  {status} {text[:30]}... -> {detected_lang} (Expected: {expected_lang})")
    
    # Test translation
    print("\n🔄 Translation Tests:")
    translation_tests = [
        ("Hello, how are you?", "en", "hi"),
        ("मुझे सिरदर्द है", "hi", "en"),
        ("எனக்கு தலைவலி உண்டு", "ta", "en")
    ]
    
    for text, source, target in translation_tests:
        translated = service.translate_text(text, source, target)
        print(f"  {source} -> {target}: {text}")
        print(f"  Translated: {translated}")
        print()

if __name__ == "__main__":
    test_translation_service()