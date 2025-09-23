"""
Real Translation Service - Multilingual Support for Indian Languages
"""
import logging
from typing import Dict, Any, Optional
import re
import requests

logger = logging.getLogger(__name__)

class RealTranslationService:
    """Real translation service for Indian languages"""
    
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
        
        # Language detection patterns using Unicode ranges
        self.language_patterns = {
            "hi": r"[\u0900-\u097F]",      # Devanagari (Hindi, Marathi, etc.)
            "ta": r"[\u0B80-\u0BFF]",      # Tamil
            "te": r"[\u0C00-\u0C7F]",      # Telugu
            "ml": r"[\u0D00-\u0D7F]",      # Malayalam
            "kn": r"[\u0C80-\u0CFF]",      # Kannada
            "bn": r"[\u0980-\u09FF]",      # Bengali
            "gu": r"[\u0A80-\u0AFF]",      # Gujarati
            "mr": r"[\u0900-\u097F]",      # Marathi (shares Devanagari)
            "pa": r"[\u0A00-\u0A7F]",      # Punjabi
            "or": r"[\u0B00-\u0B7F]",      # Odia
            "as": r"[\u0980-\u09FF]",      # Assamese (shares Bengali)
            "ur": r"[\u0600-\u06FF]"       # Urdu (Arabic script)
        }
        
        logger.info(f"✅ Real Translation Service initialized - Supported languages: {len(self.supported_languages)}")
    
    def detect_language(self, text: str) -> str:
        """
        Detect language using Unicode patterns
        
        Args:
            text: Input text to analyze
            
        Returns:
            Language code (ISO 639-1)
        """
        try:
            text_clean = text.strip()
            
            # Check for each language using Unicode ranges
            for lang_code, pattern in self.language_patterns.items():
                if re.search(pattern, text_clean):
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
            logger.error(f"❌ Error detecting language: {e}")
            return "en"
    
    def get_language_name(self, lang_code: str) -> str:
        """Get full language name from code"""
        return self.supported_languages.get(lang_code, "Unknown")
    
    def generate_multilingual_response(self, intent: str, confidence: float, 
                                     detected_language: str = "en") -> str:
        """
        Generate response in user's language
        
        Args:
            intent: Detected intent
            confidence: Confidence score
            detected_language: User's language
            
        Returns:
            Response in user's language
        """
        try:
            # Generate response based on intent and language
            if detected_language == "hi":  # Hindi
                return self._generate_hindi_response(intent, confidence)
            elif detected_language == "ta":  # Tamil
                return self._generate_tamil_response(intent, confidence)
            elif detected_language == "te":  # Telugu
                return self._generate_telugu_response(intent, confidence)
            elif detected_language == "ml":  # Malayalam
                return self._generate_malayalam_response(intent, confidence)
            elif detected_language == "kn":  # Kannada
                return self._generate_kannada_response(intent, confidence)
            elif detected_language == "bn":  # Bengali
                return self._generate_bengali_response(intent, confidence)
            elif detected_language == "gu":  # Gujarati
                return self._generate_gujarati_response(intent, confidence)
            elif detected_language == "mr":  # Marathi
                return self._generate_marathi_response(intent, confidence)
            elif detected_language == "pa":  # Punjabi
                return self._generate_punjabi_response(intent, confidence)
            elif detected_language == "or":  # Odia
                return self._generate_odia_response(intent, confidence)
            elif detected_language == "as":  # Assamese
                return self._generate_assamese_response(intent, confidence)
            elif detected_language == "ur":  # Urdu
                return self._generate_urdu_response(intent, confidence)
            else:  # English (default)
                return self._generate_english_response(intent, confidence)
                
        except Exception as e:
            logger.error(f"❌ Error generating multilingual response: {e}")
            return self._generate_english_response(intent, confidence)
    
    def _generate_english_response(self, intent: str, confidence: float) -> str:
        """Generate English response"""
        if intent == "emergency":
            return (
                "🚨 EMERGENCY ALERT!\n\n"
                "⚠️  Based on your symptoms, this may require immediate medical attention!\n\n"
                "✅ IMMEDIATE ACTIONS:\n"
                "• CALL EMERGENCY SERVICES (108) IMMEDIATELY\n"
                "• DO NOT DRIVE YOURSELF TO HOSPITAL\n"
                "• STAY CALM and sit comfortably\n"
                "• LOOSEN TIGHT CLOTHING\n"
                "• INFORM FAMILY MEMBERS\n"
                "• NOTE WHEN SYMPTOMS STARTED\n\n"
                "⏱️ TIME IS CRITICAL - Act immediately!\n\n"
                "💡 This is AI-generated advice. Always consult a qualified healthcare professional for medical decisions!"
            )
        elif intent == "symptom_inquiry":
            return (
                "🏥 Symptom Analysis:\n\n"
                "📋 Common Management:\n"
                "• Rest and adequate hydration\n"
                "• Monitor symptom progression\n"
                "• Maintain good nutrition\n\n"
                "⚠️  SEEK MEDICAL CARE IF:\n"
                "• Symptoms worsen or persist > 3 days\n"
                "• High fever develops\n"
                "• Severe pain occurs\n"
                "• Breathing difficulties\n"
                "• Chest pain or pressure\n\n"
                "💊 OVER-THE-COUNTER RELIEF:\n"
                "• Paracetamol for pain/fever\n"
                "• Ibuprofen for inflammation\n"
                "(Follow package directions)\n\n"
                "📞 Consult healthcare provider for persistent symptoms!"
            )
        else:
            return (
                "🏥 General Health Guidance:\n\n"
                "✅ HEALTHY LIFESTYLE TIPS:\n"
                "• Stay hydrated (8 glasses daily)\n"
                "• Exercise 30 minutes daily\n"
                "• Eat balanced nutritious meals\n"
                "• Get 7-8 hours quality sleep\n"
                "• Practice good hygiene\n"
                "• Manage stress effectively\n\n"
                "⚠️  WHEN TO CONSULT HEALTHCARE PROVIDER:\n"
                "• Persistent symptoms > 3 days\n"
                "• Unexplained weight changes\n"
                "• Chronic pain or discomfort\n"
                "• Abnormal vital signs\n"
                "• Concerning test results\n\n"
                "📞 Emergency: Call 108\n"
                "🏥 Routine Care: Contact your doctor\n"
                "💊 Pharmacy: For minor ailments\n\n"
                "💡 This is general guidance - individual needs vary!"
            )
    
    def _generate_hindi_response(self, intent: str, confidence: float) -> str:
        """Generate Hindi response"""
        if intent == "emergency":
            return (
                "🚨 आपातकालीन चेतावनी!\n\n"
                "⚠️  आपके लक्षणों के आधार पर, इसे तुरंत चिकित्सा ध्यान देने की आवश्यकता हो सकती है!\n\n"
                "✅ तुरंत कार्रवाई:\n"
                "• तुरंत आपातकालीन सेवाओं को कॉल करें (108)\n"
                "• अस्पताल में खुद को ड्राइव न करें\n"
                "• शांत रहें और आराम से बैठें\n"
                "• तंग कपड़े ढीले करें\n"
                "• परिवार के सदस्यों को सूचित करें\n"
                "• लक्षणों के शुरू होने का समय नोट करें\n\n"
                "⏱️ समय महत्वपूर्ण है - तुरंत कार्रवाई करें!\n\n"
                "💡 यह AI-जनित सलाह है। चिकित्सा निर्णयों के लिए हमेशा योग्य स्वास्थ्य देखभाल पेशेवर से परामर्श लें!"
            )
        elif intent == "symptom_inquiry":
            return (
                "🏥 लक्षण विश्लेषण:\n\n"
                "📋 सामान्य प्रबंधन:\n"
                "• आराम और पर्याप्त जलयोजन\n"
                "• लक्षण प्रगति की निगरानी\n"
                "• अच्छा पोषण बनाए रखें\n\n"
                "⚠️  चिकित्सा देखभाल कब लें:\n"
                "• लक्षण बिगड़ते हैं या 3 दिनों से अधिक समय तक रहते हैं\n"
                "• उच्च बुखार विकसित होता है\n"
                "• गंभीर दर्द होता है\n"
                "• सांस लेने में कठिनाई\n"
                "• छाती में दर्द या दबाव\n\n"
                "💊 ओवर-द-काउंटर राहत:\n"
                "• पैरासिटामोल दर्द/बुखार के लिए\n"
                "• इबुप्रोफेन सूजन के लिए\n"
                "(पैकेज निर्देशों का पालन करें)\n\n"
                "📞 लगातार लक्षणों के लिए स्वास्थ्य देखभाल प्रदाता से परामर्श लें!"
            )
        else:
            return (
                "🏥 सामान्य स्वास्थ्य मार्गदर्शन:\n\n"
                "✅ स्वस्थ जीवनशैली युक्तियाँ:\n"
                "• जलयोजन बनाए रखें (दिन में 8 गिलास)\n"
                "• दैनिक 30 मिनट व्यायाम करें\n"
                "• संतुलित पौष्टिक भोजन करें\n"
                "• 7-8 घंटे गुणवत्ता वाली नींद लें\n"
                "• अच्छी स्वच्छता का अभ्यास करें\n"
                "• तनाव का प्रभावी रूप से प्रबंधन करें\n\n"
                "⚠️  स्वास्थ्य देखभाल प्रदाता कब संपर्क करें:\n"
                "• लगातार लक्षण 3 दिनों से अधिक\n"
                "• अव्याख्यात वजन परिवर्तन\n"
                "• पुराना दर्द या असहजता\n"
                "• असामान्य महत्वपूर्ण संकेत\n"
                "• चिंताजनक परीक्षण परिणाम\n\n"
                "📞 आपातकाल: 108 कॉल करें\n"
                "🏥 नियमित देखभाल: अपने डॉक्टर से संपर्क करें\n"
                "💊 फार्मेसी: छोटी बीमारियों के लिए\n\n"
                "💡 यह सामान्य मार्गदर्शन है - व्यक्तिगत आवश्यकताएँ अलग-अलग होती हैं!"
            )
    
    def _generate_tamil_response(self, intent: str, confidence: float) -> str:
        """Generate Tamil response"""
        if intent == "emergency":
            return (
                "🚨 அவசரநிலை எச்சரிக்கை!\n\n"
                "⚠️  உங்கள் அறிகுறிகளின் அடிப்படையில், இது உடனடி மருத்துவ கவனத்தைத் தேவைப்படலாம்!\n\n"
                "✅ உடனடி நடவடிக்கைகள்:\n"
                "• உடனடி அவசரநிலை சேவைகளை அழைக்கவும் (108)\n"
                "• மருத்துவமனைக்கு தாங்களாகவே ஓட்டுவதைத் தவிர்க்கவும்\n"
                "• அமைதியாக இருங்கள் மற்றும் வசதியாக உட்காருங்கள்\n"
                "• இறுக்கமான ஆடைகளை தளர்த்துங்கள்\n"
                "• குடும்ப உறுப்பினர்களை தெரிவியுங்கள்\n"
                "• அறிகுறிகள் தொடங்கிய நேரத்தை குறிப்பிடுங்கள்\n\n"
                "⏱️ நேரம் முக்கியம் - உடனடியாக செயல்படுங்கள்!\n\n"
                "💡 இது AI-உருவாக்கப்பட்ட ஆலோசனை. மருத்துவ முடிவுகளுக்கு எப்போதும் தகுதியுள்ள மருத்துவ தொழில் நிபுணரிடம் ஆலோசனை பெறுங்கள்!"
            )
        elif intent == "symptom_inquiry":
            return (
                "🏥 அறிகுறி பகுப்பாய்வு:\n\n"
                "📋 பொதுவான மேலாண்மை:\n"
                "• ஓய்வு மற்றும் போதுமான நீர்ப்பானம்\n"
                "• அறிகுறி முன்னேற்றத்தைக் கண்காணிக்கவும்\n"
                "• நல்ல ஊட்டச்சத்து பராமரிக்கவும்\n\n"
                "⚠️  எப்போது மருத்துவ கவனம் தேவை:\n"
                "• அறிகுறிகள் மோசமாகும் அல்லது 3 நாட்களுக்கு மேல் நீடிக்கும்\n"
                "• உயர் காய்ச்சல் ஏற்படுகிறது\n"
                "• கடும் வலி ஏற்படுகிறது\n"
                "• சுவாச சிரமம்\n"
                "• மார்பக வலி அல்லது அழுத்தம்\n\n"
                "💊 ஓவர்-தி-கவுண்டர் மருந்து:\n"
                "• வலி/காய்ச்சலுக்கு பாராசிட்டமோல்\n"
                "• வீக்கத்திற்கு இபுபுரோஃபென்\n"
                "(பேக்கேஜ் வழிமுறைகளைப் பின்பற்றவும்)\n\n"
                "📞 தொடர்ச்சியான அறிகுறிகளுக்கு மருத்துவ தொழில் நிபுணரிடம் ஆலோசனை பெறுங்கள்!"
            )
        else:
            return (
                "🏥 பொதுவான சுகாதார வழிகாட்டுதல்:\n\n"
                "✅ ஆரோக்கியமான வாழ்க்கைமுறை குறிப்புகள்:\n"
                "• நீர்ப்பானம் பராமரிக்கவும் (தினம் 8 கிளாஸ்கள்)\n"
                "• தினமும் 30 நிமிடங்கள் உடற்பயிற்சி செய்யுங்கள்\n"
                "• சமநிலையான போஷ்டிகரமான உணவு சாப்பிடுங்கள்\n"
                "• 7-8 மணி தரம் உயர்ந்த தூக்கம் எடுக்கவும்\n"
                "• நல்ல சுத்தம் பராமரிக்கவும்\n"
                "• மனஅழுத்தத்தை பிரபலமாக நிர்வகிக்கவும்\n\n"
                "⚠️  எப்போது மருத்துவ தொழில் நிபுணரை தொடர்பு கொள்ள வேண்டும்:\n"
                "• தொடர்ச்சியான அறிகுறிகள் 3 நாட்களுக்கு மேல்\n"
                "• விளங்காத எடை மாற்றங்கள்\n"
                "• நிலையான வலி அல்லது அசுகரம்\n"
                "• அசாதாரண முக்கிய அறிகுறிகள்\n"
                "• கவலைக்கிடமான சோதனை முடிவுகள்\n\n"
                "📞 அவசரநிலை: 108ஐ அழைக்கவும்\n"
                "🏥 வழக்கமான கவனம்: உங்கள் டாக்டரைத் தொடர்பு கொள்ளுங்கள்\n"
                "💊 மருந்தகம்: சிறிய நோய்களுக்கு\n\n"
                "💡 இது பொதுவான வழிகாட்டுதல் - தனிப்பட்ட தேவைகள் வேறுபடுகின்றன!"
            )
    
    # Add similar methods for other languages...
    def _generate_telugu_response(self, intent: str, confidence: float) -> str:
        """Generate Telugu response"""
        if intent == "emergency":
            return (
                "🚨 ఎమర్జెన్సీ హెచ్చరిక!\n\n"
                "⚠️  మీ లక్షణాల ఆధారంగా, ఇది తక్షణ మెడికల్ శ్రద్ధ అవసరం!\n\n"
                "✅ తక్షణ చర్యలు:\n"
                "• తక్షణ ఎమర్జెన్సీ సేవలను కాల్ చేయండి (108)\n"
                "• హాస్పిటల్‌కు మీరు స్వయంగా డ్రైవ్ చేయకండి\n"
                "• శాంతంగా ఉండండి మరియు వదులుగా కూర్చోండి\n"
                "• టైట్ దుస్తులను సడలించండి\n"
                "• కుటుంబ సభ్యులను తెలియజేయండి\n"
                "• లక్షణాలు ప్రారంభమైన సమయాన్ని గమనించండి\n\n"
                "⏱️ సమయం ప్రాధాన్యత కలిగి - తక్షణమే చర్య తీసుకోండి!\n\n"
                "💡 ఇది AI-జనరేటెడ్ సలహా. మెడికల్ నిర్ణయాల కోసం ఎల్లప్పుడూ తగిన హెల్త్‌కేర్ ప్రొఫెషనల్‌తో సంప్రదించండి!"
            )
        elif intent == "symptom_inquiry":
            return (
                "🏥 లక్షణాల విశ్లేషణ:\n\n"
                "📋 సాధారణ నిర్వహణ:\n"
                "• విశ్రాంతి మరియు సరిపోతు జలకుంభం\n"
                "• లక్షణాల ప్రగతిని పర్యవేక్షించండి\n"
                "• మంచి పోషకాహారం కొనసాగించండి\n\n"
                "⚠️  ఎప్పుడు మెడికల్ కేర్ తీసుకోవాలి:\n"
                "• లక్షణాలు మోశం అవుతాయి లేదా 3 రోజులు పైగా ఉంటాయి\n"
                "• అధిక జ్వరం ఏర్పడుతుంది\n"
                "• తీవ్రమైన నొప్పి ఏర్పడుతుంది\n"
                "• శ్వాస సమస్యలు\n"
                "• ఛాతీ నొప్పి లేదా ఒత్తిడి\n\n"
                "💊 ఓవర్-ది-కౌంటర్ ఉపశమనం:\n"
                "• నొప్పి/జ్వరం కోసం పారాసిటామోల్\n"
                "• వ్యాధి కోసం ఇబుప్రోఫెన్\n"
                "(ప్యాకేజీ సూచనలను అనుసరించండి)\n\n"
                "📞 నిరంతర లక్షణాల కోసం హెల్త్‌కేర్ ప్రొవైడర్‌తో సంప్రదించండి!"
            )
        else:
            return (
                "🏥 సాధారణ హెల్త్ మార్గదర్శకం:\n\n"
                "✅ ఆరోగ్యకరమైన జీవన శైలి సూచనలు:\n"
                "• జలకుంభం కొనసాగించండి (రోజుకు 8 గ్లాసులు)\n"
                "• రోజుకు 30 నిమిషాలు వ్యాయామం చేయండి\n"
                "• సమతుల్యమైన పోషకాహార భోజనం చేయండి\n"
                "• 7-8 గంటల నాణ్యమైన నిద్ర పొందండి\n"
                "• మంచి శుభ్రత అభ్యాసం చేయండి\n"
                "• ఒత్తిడిని ప్రభావవంతంగా నిర్వహించండి\n\n"
                "⚠️  ఎప్పుడు హెల్త్‌కేర్ ప్రొవైడర్‌ను సంప్రదించాలి:\n"
                "• నిరంతర లక్షణాలు 3 రోజులు పైగా\n"
                "• వివరణ లేని బరువు మార్పులు\n"
                "• దీర్ఘకాలిక నొప్పి లేదా అసౌకర్యం\n"
                "• అసాధారణ ప్రధాన సూచనలు\n"
                "• కాంతి పరీక్ష ఫలితాలు\n\n"
                "📞 ఎమర్జెన్సీ: 108 కాల్ చేయండి\n"
                "🏥 సాధారణ కేర్: మీ డాక్టర్‌ను సంప్రదించండి\n"
                "💊 ఫార్మసీ: చిన్న అనారోగ్యాల కోసం\n\n"
                "💡 ఇది సాధారణ మార్గదర్శకం - వ్యక్తిగత అవసరాలు వేరుగా ఉంటాయి!"
            )
    
    # Add similar methods for other languages (Malayalam, Kannada, Bengali, etc.)
    def _generate_malayalam_response(self, intent: str, confidence: float) -> str:
        """Generate Malayalam response"""
        return self._generate_english_response(intent, confidence)  # Fallback for now
    
    def _generate_kannada_response(self, intent: str, confidence: float) -> str:
        """Generate Kannada response"""
        return self._generate_english_response(intent, confidence)  # Fallback for now
    
    def _generate_bengali_response(self, intent: str, confidence: float) -> str:
        """Generate Bengali response"""
        return self._generate_english_response(intent, confidence)  # Fallback for now
    
    def _generate_gujarati_response(self, intent: str, confidence: float) -> str:
        """Generate Gujarati response"""
        return self._generate_english_response(intent, confidence)  # Fallback for now
    
    def _generate_marathi_response(self, intent: str, confidence: float) -> str:
        """Generate Marathi response"""
        return self._generate_english_response(intent, confidence)  # Fallback for now
    
    def _generate_punjabi_response(self, intent: str, confidence: float) -> str:
        """Generate Punjabi response"""
        return self._generate_english_response(intent, confidence)  # Fallback for now
    
    def _generate_odia_response(self, intent: str, confidence: float) -> str:
        """Generate Odia response"""
        return self._generate_english_response(intent, confidence)  # Fallback for now
    
    def _generate_assamese_response(self, intent: str, confidence: float) -> str:
        """Generate Assamese response"""
        return self._generate_english_response(intent, confidence)  # Fallback for now
    
    def _generate_urdu_response(self, intent: str, confidence: float) -> str:
        """Generate Urdu response"""
        return self._generate_english_response(intent, confidence)  # Fallback for now
    
    def _basic_intent_detection(self, text: str) -> Dict[str, Any]:
        """Basic intent detection when models fail"""
        text_lower = text.lower()
        
        # Emergency detection
        emergency_keywords = [
            "severe chest pain", "difficulty breathing", "unconscious", 
            "stroke", "heart attack", "bleeding", "emergency"
        ]
        if any(keyword in text_lower for keyword in emergency_keywords):
            return {
                "intent": "emergency",
                "confidence": 0.95,
                "model_used": "basic",
                "symptoms": self._extract_symptoms(text_lower),
                "diseases": self._extract_diseases(text_lower),
                "entities": []
            }
        
        # Symptom detection
        symptom_keywords = [
            "headache", "fever", "cough", "pain", "nausea", "vomiting",
            "dizziness", "fatigue", "rash", "swelling"
        ]
        if any(keyword in text_lower for keyword in symptom_keywords):
            return {
                "intent": "symptom_inquiry",
                "confidence": 0.85,
                "model_used": "basic",
                "symptoms": self._extract_symptoms(text_lower),
                "diseases": self._extract_diseases(text_lower),
                "entities": []
            }
        
        # Disease detection
        disease_keywords = [
            "diabetes", "hypertension", "cancer", "malaria", "dengue",
            "covid", "flu", "influenza", "asthma", "arthritis"
        ]
        if any(keyword in text_lower for keyword in disease_keywords):
            return {
                "intent": "disease_inquiry",
                "confidence": 0.80,
                "model_used": "basic",
                "symptoms": self._extract_symptoms(text_lower),
                "diseases": self._extract_diseases(text_lower),
                "entities": []
            }
        
        # Default general health
        return {
            "intent": "general_health",
            "confidence": 0.70,
            "model_used": "basic",
            "symptoms": [],
            "diseases": [],
            "entities": []
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

# Create service instance
healthcare_service = MultilingualHealthcareService()

# Test function
def test_multilingual_service():
    """Test multilingual healthcare service"""
    print("🧪 Testing Multilingual Healthcare Service")
    print("=" * 45)
    
    service = MultilingualHealthcareService()
    
    # Test cases in different languages
    test_cases = [
        {
            "language": "English",
            "code": "en",
            "text": "I have severe chest pain and difficulty breathing"
        },
        {
            "language": "Hindi",
            "code": "hi", 
            "text": "मुझे सिरदर्द और बुखार है"
        },
        {
            "language": "Tamil",
            "code": "ta",
            "text": "எனக்கு தலைவலி மற்றும் காய்ச்சல் உண்டு"
        },
        {
            "language": "Telugu",
            "code": "te",
            "text": "నాకు తలనొప్పి మరియు జ్వరం ఉంది"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing {case['language']} ({case['code']}):")
        print(f"   Text: {case['text']}")
        
        # Detect language
        detected_lang = service.detect_language(case['text'])
        print(f"   Detected language: {detected_lang}")
        
        # Process query
        result = service.process_healthcare_query(case['text'], case['code'])
        print(f"   Intent: {result.intent} ({result.confidence:.0%})")
        print(f"   Language: {result.language}")
        print(f"   Model: {result.model_used}")
        print(f"   Response preview: {result.answer[:100]}...")
        print(f"   Processing time: {result.processing_time:.3f}s")
    
    print("\n🎉 Multilingual service test completed!")

if __name__ == "__main__":
    test_multilingual_service()