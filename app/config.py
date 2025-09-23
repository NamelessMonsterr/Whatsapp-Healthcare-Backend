"""
Application configuration module - WITH TWILIO SUPPORT
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application settings with security best practices and Twilio support"""
    
    # WhatsApp Configuration (Facebook)
    whatsapp_token: str = ""  # Keep empty, load from secure env
    whatsapp_phone_number_id: str = ""  # Keep empty, load from secure env
    whatsapp_business_account_id: Optional[str] = None
    verify_token: str = "healthcare_bot_verify_secure_123"  # Strong default
    
    # Twilio Configuration ✅ ADDED TWILIO SUPPORT
    twilio_account_sid: Optional[str] = None  # Twilio Account SID
    twilio_auth_token: Optional[str] = None   # Twilio Auth Token
    twilio_sms_number: Optional[str] = None   # Twilio SMS Number
    twilio_verify_token: str = "healthcare_bot_twilio_verify_secure_123"  # Twilio Verify Token
    
    # Database
    database_url: str = "sqlite:///./healthcare.db"
    database_echo: bool = False
    
    # Hugging Face - Optional for public models
    huggingface_token: Optional[str] = None
    model_cache_dir: str = "./data/models"
    
    # Server
    app_name: str = "Healthcare WhatsApp Chatbot"
    app_version: str = "1.0.0"
    debug: bool = True
    log_level: str = "INFO"
    port: int = 5000
    host: str = "0.0.0.0"
    
    # ML Models
    use_gpu: bool = False  # Safer default
    model_device: str = "cpu"  # Safer default
    max_length: int = 512
    batch_size: int = 1
    
    # Security - MUST CHANGE IN PRODUCTION
    secret_key: str = "change-this-to-a-very-long-random-secret-key-in-production-32-chars-minimum"
    
    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 60
    
    # Ngrok (for local development)
    ngrok_auth_token: Optional[str] = None
    ngrok_url: Optional[str] = None
    
    # Data.gov.in API Integration
    data_gov_api_key: str = "579b464db66ec23bdd00000194bfbd293c9a4ada4ea609e6695b36e0"
    data_gov_base_url: str = "https://api.data.gov.in/resource/"
    
    # Model configurations
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
        # Protect against accidental exposure
        protected_namespaces = ("settings_",)
        extra = "ignore"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories if they don't exist
        Path(self.model_cache_dir).mkdir(parents=True, exist_ok=True)
        Path("logs").mkdir(exist_ok=True)
        Path("data").mkdir(exist_ok=True)
        
        # Security validation
        self._validate_security()
    
    def _validate_security(self):
        """Validate security settings"""
        if self.secret_key == "change-this-to-a-very-long-random-secret-key-in-production-32-chars-minimum":
            if not self.debug:
                raise ValueError("Security Error: Secret key must be changed in production!")
        
        # Warn about insecure defaults in non-debug mode
        if not self.debug:
            if not self.whatsapp_token:
                print("⚠️  Warning: WhatsApp token not set")
            if self.use_gpu and self.model_device == "cpu":
                print("⚠️  Warning: GPU enabled but device set to CPU")
            if not self.twilio_account_sid:
                print("⚠️  Warning: Twilio not configured (optional)")

# Create settings instance
settings = Settings()

# ML Model configurations
ML_MODELS = {
    "multilingual": {
        "name": "ai4bharat/IndicBERTv2-MLM-only",
        "task": "feature-extraction",
        "description": "Multilingual understanding for Indian languages"
    },
    "biomedical": {
        "name": "dmis-lab/biobert-base-cased-v1.1",
        "task": "question-answering",
        "description": "Biomedical Q&A and classification"
    },
    "chatdoctor": {
        "name": "microsoft/BioGPT-Large",
        "task": "text-generation",
        "description": "Conversational medical Q&A"
    }
}

# Common Data.gov.in Resource IDs (you'll need to find actual ones)
DATAGOV_RESOURCES = {
    "hospitals": "hospital-directory-resource-id",  # Replace with actual
    "diseases": "disease-outbreak-resource-id",     # Replace with actual
    "medicines": "medicine-availability-resource-id", # Replace with actual
    "doctors": "doctor-directory-resource-id"      # Replace with actual
}