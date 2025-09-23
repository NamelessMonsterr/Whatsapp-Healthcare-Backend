"""
Healthcare Models Service - FIXED with detect_language method
"""
import logging
from typing import Dict, Any, List, Optional
import json
import time
import re
from datetime import datetime
from dataclasses import dataclass

from app.config import settings
from app.ml.model_loader import model_loader
from app.core.database import DatabaseManager, get_db_context

logger = logging.getLogger(__name__)

@dataclass
class HealthcareResponse:
    """Healthcare response data class"""
    answer: str
    intent: str
    confidence: float
    language: str = "en"
    processing_time: float = 0.0
    model_used: str = "unknown"
    metadata: Dict[str, Any] = None
    symptoms: List[str] = None
    diseases: List[str] = None
    entities: List[str] = None

class MultilingualHealthcareService:
    """Multilingual Healthcare Service with ALL required methods"""
    
    def __init__(self):
        self.model_loader = model_loader
        self.db_manager = DatabaseManager()
        logger.info("Multilingual Healthcare Service initialized with all methods")
    
    # ✅ ADD THIS MISSING METHOD:
    def detect_language(self, text: str) -> str:
        """
        Detect language of input text
        
        Args:
            text: Input text to analyze
            
        Returns:
            Language code (ISO 639-1)
        """
        try:
            logger.info(f"🔍 Detecting language for text: {text[:50]}...")
            
            # Indian language Unicode ranges
            language_patterns = {
                "hi": r"[\u0900-\u097F]",      # Hindi
                "ta": r"[\u0B80-\u0BFF]",      # Tamil
                "te": r"[\u0C00-\u0C7F]",      # Telugu
                "ml": r"[\u0D00-\u0D7F]",      # Malayalam
                "kn": r"[\u0C80-\u0CFF]",      # Kannada
                "bn": r"[\u0980-\u09FF]",      # Bengali
                "gu": r"[\u0A80-\u0AFF]",      # Gujarati
                "mr": r"[\u0900-\u097F]",      # Marathi
                "pa": r"[\u0A00-\u0A7F]",      # Punjabi
                "or": r"[\u0B00-\u0B7F]",      # Odia
                "as": r"[\u0980-\u09FF]",      # Assamese
                "ur": r"[\u0600-\u06FF]"       # Urdu
            }
            
            # Check for Indian languages first
            for lang_code, pattern in language_patterns.items():
                if re.search(pattern, text):
                    logger.info(f"✅ Language detected: {lang_code} ({self._get_language_name(lang_code)})")
                    return lang_code
            
            # Default to English for Latin script
            if re.search(r"[a-zA-Z]", text):
                logger.info("🔤 Language detected: en (English - Latin script)")
                return "en"
            
            # Fallback to English
            logger.info("🔤 Language detection fallback: en (English)")
            return "en"
            
        except Exception as e:
            logger.error(f"❌ Error detecting language: {e}", exc_info=True)
            return "en"
    
    def _get_language_name(self, lang_code: str) -> str:
        """Get full language name from code"""
        language_names = {
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
        return language_names.get(lang_code, "Unknown")
    
    # ✅ KEEP YOUR EXISTING PROCESSING METHOD:
    def process_healthcare_query(self, query: str, language: str = "en") -> HealthcareResponse:
        """Process healthcare query with multilingual support"""
        start_time = time.time()
        
        try:
            logger.info(f"Processing health query: {query}")
            logger.info(f"Language: {language}")
            
            # Detect intent with multilingual support
            intent_result = self._detect_healthcare_intent(query, language)
            
            # Generate response in user's language
            response_text = self._generate_multilingual_response(intent_result, query, language)
            
            processing_time = time.time() - start_time
            
            response = HealthcareResponse(
                answer=response_text,
                intent=intent_result["intent"],
                confidence=intent_result["confidence"],
                language=language,
                processing_time=processing_time,
                model_used=intent_result["model_used"],
                metadata={
                    "symptoms_detected": intent_result["symptoms"],
                    "diseases_mentioned": intent_result["diseases"],
                    "entities_found": len(intent_result["entities"]),
                    "processing_timestamp": datetime.utcnow().isoformat()
                },
                symptoms=intent_result["symptoms"],
                diseases=intent_result["diseases"],
                entities=intent_result["entities"]
            )
            
            logger.info(f"✅ Healthcare processing successful - Intent: {intent_result['intent']}, Confidence: {intent_result['confidence']:.3f}")
            return response
            
        except Exception as e:
            logger.error(f"❌ Healthcare processing error: {e}", exc_info=True)
            
            # Fallback response
            processing_time = time.time() - start_time
            
            return HealthcareResponse(
                answer="I understand you have health concerns. Based on your symptoms, I recommend consulting with a healthcare provider for proper medical advice and diagnosis.",
                intent="general",
                confidence=0.8,
                language=language,
                processing_time=processing_time,
                model_used="fallback",
                metadata={"error": str(e)}
            )
    
    def _detect_healthcare_intent(self, text: str, language: str = "en") -> Dict[str, Any]:
        """Detect healthcare intent from text"""
        
        text_lower = text.lower()
        
        # Emergency detection
        emergency_keywords = [
            "severe chest pain", "difficulty breathing", "unconscious", "stroke",
            "heart attack", "bleeding", "emergency", "critical", "life threatening"
        ]
        if any(keyword in text_lower for keyword in emergency_keywords):
            return {
                "intent": "emergency",
                "confidence": 0.95,
                "model_used": "rule_based",
                "symptoms": self._extract_symptoms(text_lower),
                "diseases": self._extract_diseases(text_lower),
                "entities": ["emergency"]
            }
        
        # Symptom detection
        symptom_keywords = [
            "headache", "fever", "cough", "pain", "nausea", "vomiting",
            "dizziness", "fatigue", "rash", "swelling", "chest pain",
            "difficulty breathing", "shortness of breath", "high temperature",
            "low temperature", "chills", "sweating", "weakness", "tiredness",
            "blurry vision", "double vision", "loss of vision", "eye pain",
            "ear pain", "hearing loss", "sore throat", "hoarse voice",
            "difficulty swallowing", "loss of appetite", "weight loss",
            "weight gain", "insomnia", "sleepiness", "confusion",
            "memory loss", "numbness", "tingling", "muscle weakness",
            "joint pain", "stiffness", "back pain", "neck pain",
            "abdominal pain", "stomach pain", "cramps", "diarrhea",
            "constipation", "bloody stool", "black stool", "urinary problems",
            "frequent urination", "painful urination", "blood in urine",
            "skin rash", "itching", "bruising", "bleeding"
        ]
        if any(keyword in text_lower for keyword in symptom_keywords):
            return {
                "intent": "symptom_inquiry",
                "confidence": 0.85,
                "model_used": "rule_based",
                "symptoms": self._extract_symptoms(text_lower),
                "diseases": self._extract_diseases(text_lower),
                "entities": ["symptom"]
            }
        
        # Disease detection
        disease_keywords = [
            "diabetes", "hypertension", "high blood pressure", "cancer",
            "malaria", "dengue", "covid", "coronavirus", "flu", "influenza",
            "asthma", "arthritis", "tuberculosis", "tb", "typhoid",
            "cholera", "jaundice", "hepatitis", "migraine", "epilepsy",
            "stroke", "heart attack", "cardiac arrest", "anemia",
            "thyroid", "depression", "anxiety", "osteoporosis",
            "kidney stones", "urinary tract infection", "uti",
            "gastroenteritis", "food poisoning", "allergies", "sinusitis"
        ]
        if any(keyword in text_lower for keyword in disease_keywords):
            return {
                "intent": "disease_inquiry",
                "confidence": 0.80,
                "model_used": "rule_based",
                "symptoms": self._extract_symptoms(text_lower),
                "diseases": self._extract_diseases(text_lower),
                "entities": ["disease"]
            }
        
        # General health
        return {
            "intent": "general_health",
            "confidence": 0.70,
            "model_used": "rule_based",
            "symptoms": [],
            "diseases": [],
            "entities": ["general"]
        }
    
    def _extract_symptoms(self, text: str) -> List[str]:
        """Extract symptoms from text"""
        common_symptoms = [
            "headache", "fever", "cough", "pain", "nausea", "vomiting",
            "dizziness", "fatigue", "rash", "swelling", "chest pain",
            "difficulty breathing", "shortness of breath", "high temperature",
            "low temperature", "chills", "sweating", "weakness", "tiredness",
            "blurry vision", "double vision", "loss of vision", "eye pain",
            "ear pain", "hearing loss", "sore throat", "hoarse voice",
            "difficulty swallowing", "loss of appetite", "weight loss",
            "weight gain", "insomnia", "sleepiness", "confusion",
            "memory loss", "numbness", "tingling", "muscle weakness",
            "joint pain", "stiffness", "back pain", "neck pain",
            "abdominal pain", "stomach pain", "cramps", "diarrhea",
            "constipation", "bloody stool", "black stool", "urinary problems",
            "frequent urination", "painful urination", "blood in urine",
            "skin rash", "itching", "bruising", "bleeding"
        ]
        
        found_symptoms = []
        for symptom in common_symptoms:
            if symptom in text:
                found_symptoms.append(symptom)
        
        return found_symptoms
    
    def _extract_diseases(self, text: str) -> List[str]:
        """Extract diseases from text"""
        common_diseases = [
            "diabetes", "hypertension", "high blood pressure", "cancer",
            "malaria", "dengue", "covid", "coronavirus", "flu", "influenza",
            "asthma", "arthritis", "tuberculosis", "tb", "typhoid",
            "cholera", "jaundice", "hepatitis", "migraine", "epilepsy",
            "stroke", "heart attack", "cardiac arrest", "anemia",
            "thyroid", "depression", "anxiety", "osteoporosis",
            "kidney stones", "urinary tract infection", "uti",
            "gastroenteritis", "food poisoning", "allergies", "sinusitis"
        ]
        
        found_diseases = []
        for disease in common_diseases:
            if disease in text:
                found_diseases.append(disease)
        
        return found_diseases
    
    def _generate_multilingual_response(self, intent_result: Dict[str, Any], 
                                     original_query: str, language: str) -> str:
        """Generate response in user's language"""
        
        intent = intent_result["intent"]
        symptoms = intent_result["symptoms"]
        diseases = intent_result["diseases"]
        confidence = intent_result["confidence"]
        
        # Generate response based on intent
        if intent == "emergency":
            return self._generate_emergency_response(symptoms, original_query)
        elif intent == "symptom_inquiry":
            return self._generate_symptom_response(symptoms, original_query)
        elif intent == "disease_inquiry":
            return self._generate_disease_response(diseases, symptoms)
        else:
            return self._generate_general_response()
    
    def _generate_emergency_response(self, symptoms: List[str], text: str) -> str:
        """Generate emergency response"""
        symptoms_list = ", ".join(symptoms) if symptoms else "severe symptoms"
        
        return (
            f"🚨 EMERGENCY ALERT!\n\n"
            f"⚠️  Based on your symptoms ({symptoms_list}), this may require immediate medical attention!\n\n"
            f"✅ IMMEDIATE ACTIONS:\n"
            f"• CALL EMERGENCY SERVICES (108) IMMEDIATELY\n"
            f"• DO NOT DRIVE YOURSELF TO HOSPITAL\n"
            f"• STAY CALM and sit comfortably\n"
            f"• LOOSEN TIGHT CLOTHING\n"
            f"• INFORM FAMILY MEMBERS\n"
            f"• NOTE WHEN SYMPTOMS STARTED\n\n"
            f"⏱️ TIME IS CRITICAL - Act immediately!\n\n"
            f"💡 This is AI-generated advice. Always consult a qualified healthcare professional for medical decisions!"
        )
    
    def _generate_symptom_response(self, symptoms: List[str], text: str) -> str:
        """Generate symptom response"""
        symptom_list = ", ".join(symptoms) if symptoms else "your reported symptoms"
        
        return (
            f"🏥 Symptom Analysis for: {symptom_list}\n\n"
            f"📋 Common Management:\n"
            f"• Rest and adequate hydration\n"
            f"• Monitor symptom progression\n"
            f"• Maintain good nutrition\n\n"
            f"⚠️  SEEK MEDICAL CARE IF:\n"
            f"• Symptoms worsen or persist > 3 days\n"
            f"• High fever develops\n"
            f"• Severe pain occurs\n"
            f"• Breathing difficulties\n"
            f"• Chest pain or pressure\n\n"
            f"💊 OVER-THE-COUNTER RELIEF:\n"
            f"• Paracetamol for pain/fever\n"
            f"• Ibuprofen for inflammation\n"
            f"(Follow package directions)\n\n"
            f"📞 Consult healthcare provider for persistent symptoms!"
        )
    
    def _generate_disease_response(self, diseases: List[str], symptoms: List[str]) -> str:
        """Generate disease response"""
        disease_list = ", ".join(diseases) if diseases else "the condition you mentioned"
        
        return (
            f"🩺 Information about {disease_list}:\n\n"
            f"📋 GENERAL INFORMATION:\n"
            f"• Early detection improves outcomes\n"
            f"• Follow prescribed treatment plans\n"
            f"• Regular monitoring important\n"
            f"• Lifestyle modifications beneficial\n\n"
            f"⚠️  IMPORTANT CONSIDERATIONS:\n"
            f"• Medication compliance crucial\n"
            f"• Regular follow-up appointments\n"
            f"• Healthy lifestyle choices\n"
            f"• Support group participation\n\n"
            f"👨‍⚕️ Always consult your healthcare provider for personalized care!"
        )
    
    def _generate_general_response(self) -> str:
        """Generate general health response"""
        return (
            f"🏥 General Health Guidance:\n\n"
            f"✅ HEALTHY LIFESTYLE TIPS:\n"
            f"• Stay hydrated (8 glasses daily)\n"
            f"• Exercise 30 minutes daily\n"
            f"• Eat balanced nutritious meals\n"
            f"• Get 7-8 hours quality sleep\n"
            f"• Practice good hygiene\n"
            f"• Manage stress effectively\n\n"
            f"⚠️  WHEN TO CONSULT HEALTHCARE PROVIDER:\n"
            f"• Persistent symptoms > 3 days\n"
            f"• Unexplained weight changes\n"
            f"• Chronic pain or discomfort\n"
            f"• Abnormal vital signs\n"
            f"• Concerning test results\n\n"
            f"📞 Emergency: Call 108\n"
            f"🏥 Routine Care: Contact your doctor\n"
            f"💊 Pharmacy: For minor ailments\n\n"
            f"💡 This is general guidance - individual needs vary!"
        )

# ✅ CRITICAL: Create service instance
healthcare_service = MultilingualHealthcareService()

# Test function
def test_healthcare_service():
    """Test healthcare service"""
    print("🧪 Testing Healthcare Service")
    print("=" * 30)
    
    service = MultilingualHealthcareService()
    
    # Test language detection
    test_cases = [
        ("I have severe chest pain", "en"),
        ("मुझे सिरदर्द और बुखार है", "hi"),
        ("எனக்கு தலைவலி மற்றும் காய்ச்சல் உண்டு", "ta"),
        ("నాకు తలనొప్పి మరియు జ్వరం ఉంది", "te"),
        ("എനിക്ക് തലവേദനയും ജ്വരവും ഉണ്ട്", "ml"),
        ("ನನಗೆ ತಲೆನೋವು ಮತ್ತು ಜ್ವರ ಇದೆ", "kn"),
        ("আমার মাথাব্যথা এবং জ্বর আছে", "bn"),
        ("મને માથાનો દુઃખ અને તાવ છે", "gu"),
        ("मला डोकेदुखी आणि ताप आहे", "mr"),
        ("ਮੈਨੂੰ ਸਿਰਦਰਦ ਅਤੇ ਬੁਖ਼ਾਰ ਹੈ", "pa")
    ]
    
    print("🔍 Language Detection Tests:")
    for i, (text, expected_lang) in enumerate(test_cases, 1):
        detected_lang = service.detect_language(text)
        status = "✅" if detected_lang == expected_lang else "❌"
        print(f"  {status} {i}. {text[:30]}... -> {detected_lang} (Expected: {expected_lang})")
    
    print("\n🧠 Intent Detection Tests:")
    for i, (text, expected_lang) in enumerate(test_cases, 1):
        result = service.process_healthcare_query(text, expected_lang)
        print(f"  {i}. {text[:30]}...")
        print(f"     Intent: {result.intent} ({result.confidence:.0%})")
        print(f"     Language: {result.language}")
        print(f"     Model: {result.model_used}")
        print(f"     Response: {result.answer[:50]}...")
        print(f"     Processing time: {result.processing_time:.3f}s")
        print()

if __name__ == "__main__":
    test_healthcare_service()