"""
Healthcare Models Service - FIXED VERSION with Enhanced Features
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
from app.core.security import sanitize_input_string  # FIXED: Added security

logger = logging.getLogger(__name__)

@dataclass
class HealthcareResponse:
    """Healthcare response data class with enhanced metadata"""
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
    urgency_level: str = "low"  # FIXED: Added urgency level
    recommended_action: str = "consult_doctor"  # FIXED: Added recommended action

class MultilingualHealthcareService:
    """Multilingual Healthcare Service with enhanced features and security"""

    def __init__(self):
        self.model_loader = model_loader
        self.db_manager = DatabaseManager()
        logger.info("Multilingual Healthcare Service initialized with enhanced features")

    def detect_language(self, text: str) -> str:
        """
        Detect language of input text with enhanced accuracy
        
        Args:
            text: Input text to analyze
            
        Returns:
            Language code (ISO 639-1)
        """
        try:
            # FIXED: Sanitize input
            text = sanitize_input_string(text, max_length=1000)
            logger.info(f"🔍 Detecting language for text: {text[:50]}...")

            # Indian language Unicode ranges with better patterns
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

            # Check for English with better patterns
            if re.search(r"[a-zA-Z]{3,}", text):
                logger.info("🔤 Language detected: en (English - Latin script)")
                return "en"

            # Check for numbers and special characters (default to English)
            if re.search(r"[\d\W]{3,}", text):
                logger.info("🔤 Language detection fallback: en (Numbers/Special chars)")
                return "en"

            # Ultimate fallback to English
            logger.info("🔤 Language detection ultimate fallback: en (English)")
            return "en"

        except Exception as e:
            logger.error(f"❌ Error detecting language: {e}", exc_info=True)
            return "en"

    def _get_language_name(self, lang_code: str) -> str:
        """Get full language name from code with extended languages"""
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
            "ur": "Urdu",
            "sa": "Sanskrit",
            "kok": "Konkani",
            "mai": "Maithili",
            "sd": "Sindhi",
            "ne": "Nepali",
            "brx": "Bodo",
            "mni": "Manipuri",
            "sat": "Santali"
        }
        return language_names.get(lang_code, "Unknown")

    def process_healthcare_query(self, query: str, language: str = "en") -> HealthcareResponse:
        """
        Process healthcare query with multilingual support and enhanced features
        """
        start_time = time.time()

        try:
            # FIXED: Sanitize and validate input
            query = sanitize_input_string(query, max_length=1000)
            logger.info(f"Processing health query: {query[:100]}...")
            logger.info(f"Language: {language}")

            # Detect intent with multilingual support and urgency assessment
            intent_result = self._detect_healthcare_intent(query, language)
            
            # Assess urgency level
            urgency_level = self._assess_urgency_level(intent_result, query)
            
            # Determine recommended action
            recommended_action = self._determine_recommended_action(intent_result, urgency_level)

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
                    "processing_timestamp": datetime.utcnow().isoformat(),
                    "urgency_indicators": intent_result.get("urgency_indicators", []),
                    "risk_factors": intent_result.get("risk_factors", [])
                },
                symptoms=intent_result["symptoms"],
                diseases=intent_result["diseases"],
                entities=intent_result["entities"],
                urgency_level=urgency_level,
                recommended_action=recommended_action
            )

            logger.info(f"✅ Healthcare processing successful - Intent: {intent_result['intent']}, "
                       f"Confidence: {intent_result['confidence']:.3f}, Urgency: {urgency_level}")

            return response

        except Exception as e:
            logger.error(f"❌ Healthcare processing error: {e}", exc_info=True)

            # Enhanced fallback response based on urgency indicators
            processing_time = time.time() - start_time
            
            # Check for emergency indicators even in fallback
            emergency_indicators = ["emergency", "urgent", "critical", "severe", "unconscious"]
            is_emergency = any(indicator in query.lower() for indicator in emergency_indicators)
            
            if is_emergency:
                fallback_response = (
                    "🚨 Based on your message, this appears to be urgent. "
                    "Please call emergency services (108) immediately or go to the nearest hospital. "
                    "Do not wait for online assistance."
                )
                urgency = "critical"
                action = "call_emergency"
            else:
                fallback_response = (
                    "I understand you have health concerns. Based on your symptoms, "
                    "I recommend consulting with a healthcare provider for proper medical advice and diagnosis. "
                    "If this is urgent, please call 108 or visit the nearest hospital."
                )
                urgency = "low"
                action = "consult_doctor"

            return HealthcareResponse(
                answer=fallback_response,
                intent="general",
                confidence=0.5,
                language=language,
                processing_time=processing_time,
                model_used="fallback",
                metadata={"error": str(e), "fallback_reason": "processing_error"},
                urgency_level=urgency,
                recommended_action=action
            )

    def _detect_healthcare_intent(self, text: str, language: str = "en") -> Dict[str, Any]:
        """Detect healthcare intent from text with enhanced accuracy"""
        try:
            text_lower = text.lower()
            
            # FIXED: Enhanced emergency detection with more patterns
            emergency_patterns = {
                "immediate": ["severe chest pain", "difficulty breathing", "unconscious", "stroke", "heart attack"],
                "critical": ["severe bleeding", "emergency", "critical condition", "life threatening", "not breathing"],
                "urgent": ["severe pain", "high fever", "vomiting blood", "seizure", "allergic reaction"]
            }
            
            # Check for emergency indicators
            urgency_indicators = []
            risk_factors = []
            
            for urgency_level, patterns in emergency_patterns.items():
                for pattern in patterns:
                    if pattern in text_lower:
                        urgency_indicators.append(pattern)
                        if urgency_level == "immediate":
                            return {
                                "intent": "emergency",
                                "confidence": 0.98,
                                "model_used": "rule_based_emergency",
                                "symptoms": self._extract_symptoms(text_lower),
                                "diseases": self._extract_diseases(text_lower),
                                "entities": ["emergency"],
                                "urgency_indicators": urgency_indicators,
                                "risk_factors": risk_factors,
                                "urgency_level": urgency_level
                            }

            # Enhanced symptom detection with body system categorization
            symptom_categories = {
                "cardiovascular": ["chest pain", "heart pain", "irregular heartbeat", "high blood pressure"],
                "respiratory": ["cough", "difficulty breathing", "shortness of breath", "wheezing"],
                "neurological": ["headache", "dizziness", "confusion", "memory loss", "numbness"],
                "gastrointestinal": ["nausea", "vomiting", "diarrhea", "abdominal pain", "stomach pain"],
                "general": ["fever", "fatigue", "weakness", "pain", "swelling"]
            }
            
            detected_symptoms = self._extract_symptoms(text_lower)
            symptom_confidence = min(0.85 + (len(detected_symptoms) * 0.05), 0.95)
            
            if detected_symptoms:
                # Determine primary body system affected
                primary_system = self._determine_primary_body_system(detected_symptoms, symptom_categories)
                
                return {
                    "intent": "symptom_inquiry",
                    "confidence": symptom_confidence,
                    "model_used": "rule_based_symptoms",
                    "symptoms": detected_symptoms,
                    "diseases": self._extract_diseases(text_lower),
                    "entities": ["symptom"],
                    "urgency_indicators": urgency_indicators,
                    "risk_factors": risk_factors,
                    "primary_body_system": primary_system
                }

            # Enhanced disease detection
            detected_diseases = self._extract_diseases(text_lower)
            if detected_diseases:
                return {
                    "intent": "disease_inquiry",
                    "confidence": 0.82,
                    "model_used": "rule_based_diseases",
                    "symptoms": detected_symptoms,
                    "diseases": detected_diseases,
                    "entities": ["disease"],
                    "urgency_indicators": urgency_indicators,
                    "risk_factors": risk_factors
                }

            # Check for medication-related queries
            medication_keywords = ["medicine", "medication", "drug", "pill", "tablet", "capsule", "prescription"]
            if any(keyword in text_lower for keyword in medication_keywords):
                return {
                    "intent": "medication_inquiry",
                    "confidence": 0.75,
                    "model_used": "rule_based_medication",
                    "symptoms": detected_symptoms,
                    "diseases": detected_diseases,
                    "entities": ["medication"],
                    "urgency_indicators": urgency_indicators,
                    "risk_factors": risk_factors
                }

            # General health inquiry
            return {
                "intent": "general_health",
                "confidence": 0.70,
                "model_used": "rule_based_general",
                "symptoms": detected_symptoms,
                "diseases": detected_diseases,
                "entities": ["general"],
                "urgency_indicators": urgency_indicators,
                "risk_factors": risk_factors
            }

        except Exception as e:
            logger.error(f"Error detecting healthcare intent: {e}", exc_info=True)
            return {
                "intent": "general_health",
                "confidence": 0.5,
                "model_used": "fallback",
                "symptoms": [],
                "diseases": [],
                "entities": ["general"],
                "urgency_indicators": [],
                "risk_factors": []
            }

    def _determine_primary_body_system(self, symptoms: List[str], categories: Dict[str, List[str]]) -> str:
        """Determine which body system is primarily affected"""
        system_scores = {system: 0 for system in categories.keys()}
        
        for symptom in symptoms:
            for system, system_symptoms in categories.items():
                if symptom in system_symptoms:
                    system_scores[system] += 1
        
        # Return system with highest score, default to 'general'
        return max(system_scores, key=system_scores.get) if max(system_scores.values()) > 0 else "general"

    def _assess_urgency_level(self, intent_result: Dict[str, Any], query: str) -> str:
        """Assess urgency level based on intent and symptoms"""
        try:
            intent = intent_result["intent"]
            symptoms = intent_result.get("symptoms", [])
            urgency_indicators = intent_result.get("urgency_indicators", [])
            
            # Critical urgency indicators
            critical_keywords = ["emergency", "unconscious", "not breathing", "severe bleeding", "heart attack"]
            if any(keyword in query.lower() for keyword in critical_keywords):
                return "critical"
            
            # High urgency based on symptoms
            high_urgency_symptoms = ["chest pain", "difficulty breathing", "severe pain", "high fever"]
            if any(symptom in high_urgency_symptoms for symptom in symptoms):
                return "high"
            
            # Medium urgency
            medium_urgency_symptoms = ["fever", "pain", "vomiting", "diarrhea"]
            if any(symptom in medium_urgency_symptoms for symptom in symptoms):
                return "medium"
            
            # Intent-based urgency
            if intent == "emergency":
                return "critical"
            elif intent == "symptom_inquiry" and symptoms:
                return "medium"
            
            return "low"
            
        except Exception as e:
            logger.error(f"Error assessing urgency level: {e}")
            return "low"

    def _determine_recommended_action(self, intent_result: Dict[str, Any], urgency_level: str) -> str:
        """Determine recommended action based on intent and urgency"""
        try:
            intent = intent_result["intent"]
            
            # Urgency-based recommendations
            if urgency_level == "critical":
                return "call_emergency"
            elif urgency_level == "high":
                return "urgent_doctor_visit"
            elif urgency_level == "medium":
                return "schedule_appointment"
            
            # Intent-based recommendations
            if intent == "emergency":
                return "call_emergency"
            elif intent == "symptom_inquiry":
                return "monitor_symptoms"
            elif intent == "disease_inquiry":
                return "consult_specialist"
            elif intent == "medication_inquiry":
                return "consult_pharmacist"
            
            return "consult_doctor"
            
        except Exception as e:
            logger.error(f"Error determining recommended action: {e}")
            return "consult_doctor"

    def _extract_symptoms(self, text: str) -> List[str]:
        """Extract symptoms from text with enhanced patterns"""
        # FIXED: Enhanced symptom list with more medical terms
        common_symptoms = [
            # General
            "headache", "fever", "cough", "pain", "nausea", "vomiting", "fatigue", "weakness",
            "chills", "sweating", "loss of appetite", "weight loss", "weight gain", "tiredness",
            
            # Cardiovascular
            "chest pain", "heart pain", "irregular heartbeat", "high blood pressure", "palpitations",
            "shortness of breath", "difficulty breathing", "wheezing",
            
            # Respiratory
            "sore throat", "hoarse voice", "runny nose", "stuffy nose", "sinus pressure",
            "ear pain", "hearing loss", "ear discharge",
            
            # Neurological
            "dizziness", "lightheadedness", "fainting", "seizure", "tremor", "numbness", "tingling",
            "memory loss", "confusion", "difficulty concentrating", "blurry vision", "double vision",
            
            # Gastrointestinal
            "abdominal pain", "stomach pain", "cramps", "bloating", "gas", "diarrhea", "constipation",
            "heartburn", "acid reflux", "nausea", "vomiting", "difficulty swallowing",
            
            # Musculoskeletal
            "joint pain", "muscle pain", "back pain", "neck pain", "shoulder pain", "knee pain",
            "stiffness", "swelling", "muscle weakness", "muscle cramps",
            
            # Dermatological
            "skin rash", "itching", "hives", "eczema", "psoriasis", "acne", "bruising", "bleeding",
            "dry skin", "skin discoloration", "hair loss",
            
            # Genitourinary
            "urinary problems", "frequent urination", "painful urination", "blood in urine",
            "kidney pain", "bladder pain", "sexual dysfunction",
            
            # Psychological
            "anxiety", "depression", "insomnia", "sleep problems", "mood swings", "irritability",
            "panic attacks", "stress", "memory problems"
        ]

        found_symptoms = []
        text_lower = text.lower()
        
        for symptom in common_symptoms:
            if symptom in text_lower:
                found_symptoms.append(symptom)

        return found_symptoms

    def _extract_diseases(self, text: str) -> List[str]:
        """Extract diseases from text with enhanced medical conditions"""
        # FIXED: Enhanced disease list with more medical conditions
        common_diseases = [
            # Infectious diseases
            "covid", "coronavirus", "influenza", "flu", "common cold", "pneumonia", "tuberculosis", "tb",
            "malaria", "dengue", "chikungunya", "typhoid", "cholera", "hepatitis", "hiv", "aids",
            
            # Chronic conditions
            "diabetes", "hypertension", "high blood pressure", "hypotension", "low blood pressure",
            "heart disease", "cardiovascular disease", "coronary artery disease", "heart failure",
            "asthma", "chronic obstructive pulmonary disease", "copd", "bronchitis", "emphysema",
            
            # Autoimmune and inflammatory
            "arthritis", "rheumatoid arthritis", "osteoarthritis", "lupus", "multiple sclerosis",
            "inflammatory bowel disease", "crohn's disease", "ulcerative colitis", "psoriasis",
            
            # Cancer
            "cancer", "tumor", "malignancy", "leukemia", "lymphoma", "melanoma", "carcinoma",
            "breast cancer", "lung cancer", "prostate cancer", "colon cancer", "skin cancer",
            
            # Neurological
            "migraine", "epilepsy", "stroke", "parkinson's disease", "alzheimer's disease",
            "dementia", "neuropathy", "multiple sclerosis", "als",
            
            # Mental health
            "depression", "anxiety", "bipolar disorder", "schizophrenia", "ptsd", "ocd",
            "panic disorder", "social anxiety", "phobia",
            
            # Gastrointestinal
            "gastroesophageal reflux disease", "gerd", "peptic ulcer", "gallstones", "appendicitis",
            "diverticulitis", "irritable bowel syndrome", "ibs", "celiac disease",
            
            # Endocrine
            "thyroid", "hypothyroidism", "hyperthyroidism", "addison's disease", "cushing's syndrome",
            
            # Kidney and urinary
            "kidney stones", "urinary tract infection", "uti", "kidney disease", "nephritis",
            
            # Blood disorders
            "anemia", "leukemia", "lymphoma", "hemophilia", "sickle cell disease",
            
            # Allergies and immune
            "allergies", "asthma", "eczema", "hay fever", "food allergies", "drug allergies"
        ]

        found_diseases = []
        text_lower = text.lower()
        
        for disease in common_diseases:
            if disease in text_lower:
                found_diseases.append(disease)

        return found_diseases

    def _generate_multilingual_response(self, intent_result: Dict[str, Any], original_query: str, language: str) -> str:
        """Generate response in user's language with enhanced personalization"""
        try:
            intent = intent_result["intent"]
            symptoms = intent_result["symptoms"]
            diseases = intent_result["diseases"]
            confidence = intent_result["confidence"]
            urgency_level = intent_result.get("urgency_level", "low")

            # Generate response based on intent and urgency
            if intent == "emergency":
                return self._generate_emergency_response(symptoms, original_query, language, urgency_level)
            elif intent == "symptom_inquiry":
                return self._generate_symptom_response(symptoms, original_query, language, urgency_level)
            elif intent == "disease_inquiry":
                return self._generate_disease_response(diseases, symptoms, language, urgency_level)
            elif intent == "medication_inquiry":
                return self._generate_medication_response(diseases, symptoms, language)
            else:
                return self._generate_general_response(language, urgency_level)
                
        except Exception as e:
            logger.error(f"Error generating multilingual response: {e}")
            return self._generate_fallback_response(language)

    def _generate_emergency_response(self, symptoms: List[str], text: str, language: str, urgency_level: str) -> str:
        """Generate emergency response with language support and urgency-based formatting"""
        symptoms_list = ", ".join(symptoms) if symptoms else "severe symptoms"
        
        # Language-specific emergency responses
        emergency_responses = {
            "en": self._generate_english_emergency_response(symptoms_list, urgency_level),
            "hi": self._generate_hindi_emergency_response(symptoms_list, urgency_level),
            "ta": self._generate_tamil_emergency_response(symptoms_list, urgency_level),
            "te": self._generate_telugu_emergency_response(symptoms_list, urgency_level),
            "ml": self._generate_malayalam_emergency_response(symptoms_list, urgency_level),
            "kn": self._generate_kannada_emergency_response(symptoms_list, urgency_level),
            "bn": self._generate_bengali_emergency_response(symptoms_list, urgency_level)
        }
        
        return emergency_responses.get(language, emergency_responses["en"])

    def _generate_english_emergency_response(self, symptoms: str, urgency_level: str) -> str:
        """Generate English emergency response"""
        if urgency_level == "critical":
            return (
                f"🚨 CRITICAL EMERGENCY!\n\n"
                f"⚠️  Based on your symptoms ({symptoms}), this requires IMMEDIATE medical attention!\n\n"
                f"🚨 IMMEDIATE ACTIONS:\n"
                f"• CALL 108 RIGHT NOW - Do not delay!\n"
                f"• DO NOT DRIVE yourself - Get someone to drive you\n"
                f"• STAY CALM and sit/lie down comfortably\n"
                f"• LOOSEN any tight clothing\n"
                f"• INFORM family members immediately\n"
                f"• NOTE when symptoms started\n"
                f"• KEEP emergency medical information ready\n\n"
                f"⏰ EVERY SECOND COUNTS - Call now!\n\n"
                f"📞 If 108 is busy, call local hospital directly\n\n"
                f"💡 This is AI-generated emergency advice. Always follow emergency services instructions!"
            )
        else:
            return (
                f"🚨 EMERGENCY ALERT!\n\n"
                f"⚠️  Based on your symptoms ({symptoms}), this may require immediate medical attention!\n\n"
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

    def _generate_hindi_emergency_response(self, symptoms: str, urgency_level: str) -> str:
        """Generate Hindi emergency response"""
        return (
            f"🚨 आपातकालीन चेतावनी!\n\n"
            f"⚠️ आपके लक्षणों ({symptoms}) के आधार पर, इसे तत्काल चिकित्सा ध्यान की आवश्यकता हो सकती है!\n\n"
            f"✅ तत्काल कार्रवाई:\n"
            f"• आपातकालीन सेवाओं (108) को तुरंत कॉल करें\n"
            f"• खुद अस्पताल न जाएं\n"
            f"• शांत रहें और आराम से बैठें\n"
            f"• ढीले कपड़े पहनें\n"
            f"• परिवार के सदस्यों को सूचित करें\n"
            f"• नोट करें जब लक्षण शुरू हुए\n\n"
            f"⏱️ समय महत्वपूर्ण है - तुरंत कार्रवाई करें!\n\n"
            f"💡 यह AI-जनित सलाह है। हमेशा योग्य स्वास्थ्य देखभाल पेशेवर से सलाह लें!"
        )

    def _generate_tamil_emergency_response(self, symptoms: str, urgency_level: str) -> str:
        """Generate Tamil emergency response"""
        return (
            f"🚨 அவசர எச்சரிக்கை!\n\n"
            f"⚠️ உங்கள் அறிகுறிகளின் அடிப்படையில் ({symptoms}), இது உடனடி மருத்துவ கவனிப்பை தேவைப்படலாம்!\n\n"
            f"✅ உடனடி நடவடிக்கைகள்:\n"
            f"• அவசர சேவைகளுக்கு (108) உடனடியாக அழைக்கவும்\n"
            f"• நீங்களாக மருத்துவமனைக்கு செல்ல வேண்டாம்\n"
            f"• அமைதியாக இருங்கள் மற்றும் அமைதியாக அமர்ந்து கொள்ளுங்கள்\n"
            f"• தளர்வான ஆடைகளை அணியவும்\n"
            f"• குடும்ப உறுப்பினர்களுக்கு தெரியப்படுத்தவும்\n"
            f"• அறிகுறிகள் எப்போது தொடங்கின என்பதை குறிப்பிடவும்\n\n"
            f"⏱️ நேரம் முக்கியம் - உடனடியாக செயல்படவும்!\n\n"
            f"💡 இது AI-உருவாக்கிய ஆலோசனையாகும். எப்போதும் தகுதியான சுகாதார நிபுணரின் ஆலோசனையைப் பெறவும்!"
        )

    def _generate_telugu_emergency_response(self, symptoms: str, urgency_level: str) -> str:
        """Generate Telugu emergency response"""
        return (
            f"🚨 అత్యవసర హెచ్చరిక!\n\n"
            f"⚠️ మీ లక్షణాల ఆధారంగా ({symptoms}), దీనికి తక్షణ వైద్య శ్రద్ధ అవసరం కావచ్చు!\n\n"
            f"✅ తక్షణ చర్యలు:\n"
            f"• అత్యవసర సేవలకు (108) వెంటనే కాల్ చేయండి\n"
            f"• మీరే ఆసుపత్రికి వెళ్లవద్దు\n"
            f"• ప్రశాంతంగా ఉండండి మరియు సౌకర్యవంతంగా కూర్చోండి\n"
            f"• loose బట్టలు ధరించండి\n"
            f"• కుటుంబ సభ్యులకు తెలియజేయండి\n"
            f"• లక్షణాలు ఎప్పుడు ప్రారంభమయ్యాయో గుర్తించండి\n\n"
            f"⏱️ సమయం కీలకం - వెంటనే చర్య తీసుకోండి!\n\n"
            f"💡 ఇది AI-జనరేట్ చేసిన సలహా. ఎప్పుడూ అర్హత కలిగిన ఆరోగ్య సంరక్షణ వృత్తిపరుడి సలహా తీసుకోండి!"
        )

    def _generate_malayalam_emergency_response(self, symptoms: str, urgency_level: str) -> str:
        """Generate Malayalam emergency response"""
        return (
            f"🚨 അടിയന്തിര മുന്നറിയിപ്പ്!\n\n"
            f"⚠️ നിങ്ങളുടെ ലക്ഷണങ്ങളെ ആधാരമാക്കി ({symptoms}), ഇതിന് തത്ക്ഷണ വൈദിക ശ്രദ്ധ ആവശ്യമായി വന്നേക്കാം!\n\n"
            f"✅ തത്ക്ഷണ നടപടികൾ:\n"
            f"• അടിയന്തിര സേവനങ്ങൾക്ക് (108) ഉടൻ വിളിക്കുക\n"
            f"• നിങ്ങൾ തന്നെ ആശുപത്രിയിൽ പോകരുത്\n"
            f"• ശാന്തരായി ഇരിക്കുകയും സുഖമായി ഇരിക്കുകയും ചെയ്യുക\n"
            f"•宽松 വസ്ത്രങ്ങൾ ധരിക്കുക\n"
            f"• കുടുംബ അംഗങ്ങളെ അറിയിക്കുക\n"
            f"• ലക്ഷണങ്ങൾ എപ്പോൾ ആരംഭിച്ചുവെന്ന് നോക്കുക\n\n"
            f"⏱️ സമയം നിർണായകമാണ് - ഉടൻ പ്രവർത്തിക്കുക!\n\n"
            f"💡 ഇത് AI-സൃഷ്ടിച്ച ഉപദേശമാണ്. എപ്പോഴും യോഗ്യതയുള്ള ആരോഗ്യ പരിപാലന വിദഗ്ധനെ സമീപിക്കുക!"
        )

    def _generate_kannada_emergency_response(self, symptoms: str, urgency_level: str) -> str:
        """Generate Kannada emergency response"""
        return (
            f"🚨 ತುರ್ತು ಎಚ್ಚರಿಕೆ!\n\n"
            f"⚠️ ನಿಮ್ಮ ಲಕ್ಷಣಗಳ ಆಧಾರದಲ್ಲಿ ({symptoms}), ಇದಕ್ಕೆ ತಕ್ಷಣದ ವೈದ್ಯಕೀಯ ಗಮನ ಬೇಕಾಗಬಹುದು!\n\n"
            f"✅ ತಕ್ಷಣ ಕ್ರಮಗಳು:\n"
            f"• ತುರ್ತು ಸೇವೆಗಳಿಗೆ (108) ತಕ್ಷಣ ಕರೆ ಮಾಡಿ\n"
            f"• ನೀವೇ ಆಸ್ಪತ್ರೆಗೆ ಹೋಗಬೇಡಿ\n"
            f"• ಶಾಂತವಾಗಿರಿ ಮತ್ತು ಆರಾಮವಾಗಿ ಕುಳಿತುಕೊಳ್ಳಿ\n"
            f"• loose ಬಟ್ಟೆಗಳನ್ನು ಧರಿಸಿ\n"
            f"• ಕುಟುಂಬ ಸದಸ್ಯರಿಗೆ ತಿಳಿಸಿ\n"
            f"• ಲಕ್ಷಣಗಳು ಯಾವಾಗ ಪ್ರಾರಂಭವಾದವು ಎಂಬುದನ್ನು ಗಮನಿಸಿ\n\n"
            f"⏱️ ಸಮಯ ನಿರ್ಣಾಯಕವಾಗಿದೆ - ತಕ್ಷಣ ಕ್ರಿಯಾತ್ಮಕರಾಗಿ!\n\n"
            f"💡 ಇದು AI-ಜನರೇಟ್ ಮಾಡಿದ ಸಲಹೆಯಾಗಿದೆ. ಯಾವಾಗಲೂ ಅರ್ಹತೆಯ ಆರೋಗ್ಯ ರಕ್ಷಣಾ ವೃತ್ತಿಪರರ ಸಲಹೆಯನ್ನು ಪಡೆಯಿರಿ!"
        )

    def _generate_bengali_emergency_response(self, symptoms: str, urgency_level: str) -> str:
        """Generate Bengali emergency response"""
        return (
            f"🚨 জরুরি সতর্কতা!\n\n"
            f"⚠️ আপনার লক্ষণগুলির ভিত্তিতে ({symptoms}), এর জন্য তাত্ক্ষণিক চিকিৎসা যত্ন প্রয়োজন হতে পারে!\n\n"
            f"✅ তাত্ক্ষণিক পদক্ষেপ:\n"
            f"• জরুরি সেবা (108) এ তৎক্ষণাত কল করুন\n"
            f"• নিজে হাসপাতালে যাবেন না\n"
            f"• শান্ত থাকুন এবং আরাম করে বসুন\n"
            f"• loose পোশাক পরুন\n"
            f"• পরিবারের সদস্যদের জানান\n"
            f"• দেখুন লক্ষণগুলি কখন শুরু হয়েছে\n\n"
            f"⏱️ সময় গুরুত্বপূর্ণ - তৎক্ষণাত কাজ করুন!\n\n"
            f"💡 এটি AI-জেনারেটেড পরামর্শ। সর্বদা যোগ্য স্বাস্থ্যসেবা পেশাদারের পরামর্শ নিন!"
        )

    def _generate_symptom_response(self, symptoms: List[str], text: str, language: str, urgency_level: str) -> str:
        """Generate symptom response with language support"""
        symptom_list = ", ".join(symptoms) if symptoms else "your reported symptoms"
        
        responses = {
            "en": self._generate_english_symptom_response(symptom_list, urgency_level),
            "hi": self._generate_hindi_symptom_response(symptom_list, urgency_level),
            "ta": self._generate_tamil_symptom_response(symptom_list, urgency_level),
            "te": self._generate_telugu_symptom_response(symptom_list, urgency_level),
            "ml": self._generate_malayalam_symptom_response(symptom_list, urgency_level),
            "kn": self._generate_kannada_symptom_response(symptom_list, urgency_level),
            "bn": self._generate_bengali_symptom_response(symptom_list, urgency_level)
        }
        
        return responses.get(language, responses["en"])

    def _generate_english_symptom_response(self, symptoms: str, urgency_level: str) -> str:
        """Generate English symptom response based on urgency"""
        if urgency_level == "high":
            return (
                f"🏥 URGENT Symptom Assessment for: {symptoms}\n\n"
                f"⚠️  SEEK MEDICAL ATTENTION TODAY:\n"
                f"• Contact your doctor immediately\n"
                f"• Visit urgent care or emergency room\n"
                f"• Do not wait for symptoms to worsen\n\n"
                f"📋 WHILE WAITING FOR CARE:\n"
                f"• Rest and stay hydrated\n"
                f"• Monitor symptoms closely\n"
                f"• Avoid strenuous activities\n"
                f"• Keep medical information ready\n\n"
                f"🚨 Go to ER if symptoms worsen!\n\n"
                f"💡 This assessment suggests urgent medical evaluation."
            )
        else:
            return (
                f"🏥 Symptom Analysis for: {symptoms}\n\n"
                f"📋 COMMON MANAGEMENT:\n"
                f"• Rest and adequate hydration\n"
                f"• Monitor symptom progression\n"
                f"• Maintain good nutrition\n"
                f"• Apply warm/cold compresses as needed\n\n"
                f"⚠️  SEEK MEDICAL CARE IF:\n"
                f"• Symptoms worsen or persist > 3 days\n"
                f"• High fever develops (>38.5°C/101.3°F)\n"
                f"• Severe pain occurs\n"
                f"• Breathing difficulties\n"
                f"• Chest pain or pressure\n"
                f"• Confusion or disorientation\n\n"
                f"💊 OVER-THE-COUNTER RELIEF:\n"
                f"• Paracetamol for pain/fever\n"
                f"• Ibuprofen for inflammation (if no contraindications)\n"
                f"• Antihistamines for allergies\n"
                f"(Always follow package directions and consult pharmacist)\n\n"
                f"📞 Consult healthcare provider for persistent symptoms!"
            )

    def _generate_disease_response(self, diseases: List[str], symptoms: List[str], language: str, urgency_level: str) -> str:
        """Generate disease response with language support"""
        disease_list = ", ".join(diseases) if diseases else "the condition you mentioned"
        
        responses = {
            "en": self._generate_english_disease_response(disease_list, symptoms, urgency_level),
            "hi": self._generate_hindi_disease_response(disease_list, symptoms, urgency_level),
            "ta": self._generate_tamil_disease_response(disease_list, symptoms, urgency_level),
            "te": self._generate_telugu_disease_response(disease_list, symptoms, urgency_level),
            "ml": self._generate_malayalam_disease_response(disease_list, symptoms, urgency_level),
            "kn": self._generate_kannada_disease_response(disease_list, symptoms, urgency_level),
            "bn": self._generate_bengali_disease_response(disease_list, symptoms, urgency_level)
        }
        
        return responses.get(language, responses["en"])

    def _generate_english_disease_response(self, diseases: str, symptoms: List[str], urgency_level: str) -> str:
        """Generate English disease response"""
        return (
            f"🩺 Information about {diseases}:\n\n"
            f"📋 GENERAL INFORMATION:\n"
            f"• Early detection and treatment improve outcomes significantly\n"
            f"• Follow your healthcare provider's treatment plan consistently\n"
            f"• Regular monitoring and follow-up appointments are crucial\n"
            f"• Lifestyle modifications can greatly impact disease management\n"
            f"• Support groups and education help with long-term management\n\n"
            f"⚠️  IMPORTANT CONSIDERATIONS:\n"
            f"• Medication compliance is essential - never skip doses\n"
            f"• Keep regular follow-up appointments with your doctor\n"
            f"• Maintain a healthy lifestyle (diet, exercise, sleep, stress management)\n"
            f"• Consider joining patient support groups for emotional support\n"
            f"• Keep emergency contact information readily available\n"
            f"• Learn to recognize warning signs that require immediate care\n\n"
            f"📊 MONITORING & PREVENTION:\n"
            f"• Track your symptoms and share patterns with your doctor\n"
            f"• Maintain regular health screenings as recommended\n"
            f"• Keep vaccinations up to date\n"
            f"• Manage stress through relaxation techniques\n"
            f"• Maintain social connections for mental health\n\n"
            f"👨‍⚕️ Always consult your healthcare provider for personalized care and treatment decisions!"
        )

    def _generate_medication_response(self, diseases: List[str], symptoms: List[str], language: str) -> str:
        """Generate medication-related response"""
        responses = {
            "en": (
                f"💊 MEDICATION INFORMATION & SAFETY:\n\n"
                f"✅ GENERAL MEDICATION GUIDELINES:\n"
                f"• ALWAYS follow your doctor's prescription exactly\n"
                f"• Take medications at the same time each day\n"
                f"• Never skip doses or stop medications without consulting your doctor\n"
                f"• Read medication labels and leaflets carefully\n"
                f"• Store medications as directed (temperature, light, moisture)\n\n"
                f"⚠️  SAFETY PRECAUTIONS:\n"
                f"• Inform your doctor about ALL medications you take (including OTC and supplements)\n"
                f"• Ask about potential side effects and what to watch for\n"
                f"• Never share prescription medications with others\n"
                f"• Keep medications in original containers with labels\n"
                f"• Check expiration dates regularly\n\n"
                f"🚨 WHEN TO SEEK HELP:\n"
                f"• Severe side effects or allergic reactions\n"
                f"• Medication doesn't seem to be working\n"
                f"• Difficulty affording medications\n"
                f"• Questions about drug interactions\n\n"
                f"👨‍⚕️ Consult your pharmacist or doctor for specific medication questions!"
            )
        }
        
        return responses.get(language, responses["en"])

    def _generate_general_response(self, language: str, urgency_level: str) -> str:
        """Generate general health response with language support"""
        responses = {
            "en": (
                f"🏥 General Health & Wellness Guidance:\n\n"
                f"✅ DAILY HEALTH MAINTENANCE:\n"
                f"• Stay hydrated (8-10 glasses of water daily)\n"
                f"• Exercise at least 30 minutes daily (walking, yoga, swimming)\n"
                f"• Eat balanced meals with fruits, vegetables, whole grains, lean proteins\n"
                f"• Get 7-9 hours of quality sleep each night\n"
                f"• Practice good hand hygiene\n"
                f"• Manage stress through meditation, deep breathing, or hobbies\n"
                f"• Maintain social connections for mental health\n"
                f"• Avoid smoking and limit alcohol consumption\n\n"
                f"⚠️  WHEN TO CONSULT HEALTHCARE PROVIDER:\n"
                f"• Persistent symptoms lasting more than 3 days\n"
                f"• Unexplained weight loss or gain (>5% in 6 months)\n"
                f"• Chronic pain or discomfort affecting daily activities\n"
                f"• Abnormal vital signs (fever >38.5°C, BP >140/90, HR >100)\n"
                f"• Concerning test results or screening findings\n"
                f"• New or worsening mental health symptoms\n"
                f"• Medication side effects or interactions\n\n"
                f"📊 PREVENTIVE CARE:\n"
                f"• Schedule regular health check-ups\n"
                f"• Keep vaccinations up to date\n"
                f"• Monitor chronic conditions as directed\n"
                f"• Practice safe behaviors (seatbelts, helmets, safe sex)\n"
                f"• Maintain work-life balance\n\n"
                f"📞 Emergency: Call 108\n"
                f"🏥 Routine Care: Contact your primary care doctor\n"
                f"💊 Pharmacy: For minor ailments and medication questions\n"
                f"🧠 Mental Health: Reach out to counselors or support groups\n\n"
                f"💡 This is general health guidance - individual needs may vary. "
                f"Always consult healthcare providers for personalized medical advice!"
            )
        }
        
        return responses.get(language, responses["en"])

    def _generate_fallback_response(self, language: str) -> str:
        """Generate fallback response for unsupported languages"""
        return (
            f"🏥 Health Information:\n\n"
            f"I understand you have health concerns. For accurate medical advice, "
            f"please consult with a qualified healthcare provider. \n\n"
            f"If this is an emergency, call 108 immediately.\n\n"
            f"For general health guidance:\n"
            f"• Maintain healthy diet and exercise\n"
            f"• Get adequate sleep\n"
            f"• Manage stress effectively\n"
            f"• Stay hydrated\n\n"
            f"Always seek professional medical advice for health concerns."
        )

    # FIXED: Added other language response generators (abbreviated for space)
    def _generate_hindi_symptom_response(self, symptoms: str, urgency_level: str) -> str:
        return f"🏥 लक्षण विश्लेषण: {symptoms}\n\nउपरोक्त जानकारी के लिए अंग्रेजी प्रतिक्रिया देखें।"

    def _generate_tamil_symptom_response(self, symptoms: str, urgency_level: str) -> str:
        return f"🏥 லக்ஷண பகுப்பாய்வு: {symptoms}\n\nமேலே உள்ள தகவலுக்கான ஆங்கில பதிலைப் பார்க்கவும்."

    def _generate_telugu_symptom_response(self, symptoms: str, urgency_level: str) -> str:
        return f"🏥 లక్షణ విశ్లేషణ: {symptoms}\n\nపై సమాచారం కోసం ఆంగ్ల ప్రతిస్పందన చూడండి."

    def _generate_malayalam_symptom_response(self, symptoms: str, urgency_level: str) -> str:
        return f"🏥 ലക്ഷണ വിശകലനം: {symptoms}\n\nമുകളിലുള്ള വിവരങ്ങൾക്കായുള്ള ഇംഗ്ലീഷ് പ്രതികരണം കാണുക."

    def _generate_kannada_symptom_response(self, symptoms: str, urgency_level: str) -> str:
        return f"🏥 ಲಕ್ಷಣ ವಿಶ್ಲೇಷಣೆ: {symptoms}\n\nಮೇಲಿನ ಮಾಹಿತಿಗಾಗಿ ಇಂಗ್ಲಿಷ್ ಪ್ರತಿಕ್ರಿಯೆಯನ್ನು ನೋಡಿ."

    def _generate_bengali_symptom_response(self, symptoms: str, urgency_level: str) -> str:
        return f"🏥 লক্ষণ বিশ্লেষণ: {symptoms}\n\nউপরের তথ্যের জন্য ইংরেজি প্রতিক্রিয়া দেখুন."

    # Similar implementations for disease responses in other languages
    def _generate_hindi_disease_response(self, diseases: str, symptoms: List[str], urgency_level: str) -> str:
        return f"🩺 रोग जानकारी: {diseases}\n\nउपरोक्त जानकारी के लिए अंग्रेजी प्रतिक্রिया देखें।"

    def _generate_tamil_disease_response(self, diseases: str, symptoms: List[str], urgency_level: str) -> str:
        return f"🩺 நோய் தகவல்: {diseases}\n\nமேலே உள்ள தகவலுக்கான ஆங்கில பதிலைப் பார்க்கவும்."

    def _generate_telugu_disease_response(self, diseases: str, symptoms: List[str], urgency_level: str) -> str:
        return f"🩺 వ్యాధి సమాచారం: {diseases}\n\nపై సమాచారం కోసం ఆంగ్ల ప్రతిస్పందన చూడండి."

    def _generate_malayalam_disease_response(self, diseases: str, symptoms: List[str], urgency_level: str) -> str:
        return f"🩺 രോഗ വിവരം: {diseases}\n\nമുകളില
