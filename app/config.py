"""
Application configuration module - FIXED VERSION
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os
import secrets
from pathlib import Path

class Settings(BaseSettings):
    """Application settings with security best practices and Twilio support"""

    # WhatsApp Configuration (Facebook)
    whatsapp_token: str = ""
    whatsapp_phone_number_id: str = ""
    whatsapp_business_account_id: Optional[str] = None
    verify_token: str = ""

    # Twilio Configuration
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_sms_number: Optional[str] = None
    twilio_verify_token: str = ""

    # Database
    database_url: str = "sqlite+aiosqlite:///./healthcare.db"  # FIXED: Async support
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
    use_gpu: bool = False
    model_device: str = "cpu"
    max_length: int = 512
    batch_size: int = 1

    # Security - Generate random defaults if not provided
    secret_key: str = ""
    admin_api_key: str = ""

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 60

    # Admin Settings
    admin_phone_numbers: str = ""  # Comma-separated list

    # Ngrok (for local development)
    ngrok_auth_token: Optional[str] = None
    ngrok_url: Optional[str] = None

    # Data.gov.in API Integration
    data_gov_api_key: str = ""
    data_gov_base_url: str = "https://api.data.gov.in/resource/"

    # Model configurations
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        protected_namespaces = ("settings_",)
        extra = "ignore"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Generate secure defaults if not provided
        if not self.secret_key:
            self.secret_key = secrets.token_urlsafe(32)
        if not self.verify_token:
            self.verify_token = secrets.token_urlsafe(16)
        if not self.twilio_verify_token:
            self.twilio_verify_token = secrets.token_urlsafe(16)
        if not self.admin_api_key:
            self.admin_api_key = secrets.token_urlsafe(24)
            
        # Create directories if they don't exist
        Path(self.model_cache_dir).mkdir(parents=True, exist_ok=True)
        Path("logs").mkdir(exist_ok=True)
        Path("data").mkdir(exist_ok=True)

        # Security validation
        self._validate_security()

    def _validate_security(self):
        """Validate security settings"""
        if not self.debug:
            if not self.whatsapp_token:
                raise ValueError("Security Error: WhatsApp token must be set in production!")
            if len(self.secret_key) < 32:
                raise ValueError("Security Error: Secret key must be at least 32 characters!")
            if not self.database_url.startswith("postgresql"):
                print("⚠️  Warning: Using SQLite in production. Consider PostgreSQL for better performance.")

        # Validate GPU settings
        if self.use_gpu and self.model_device == "cpu":
            print("⚠️  Warning: GPU enabled but device set to CPU, switching to GPU")
            self.model_device = "cuda" if self.use_gpu else "cpu"

    @property
    def admin_phone_list(self) -> list:
        """Get admin phone numbers as list"""
        if self.admin_phone_numbers:
            return [phone.strip() for phone in self.admin_phone_numbers.split(",") if phone.strip()]
        return []

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

# Common Data.gov.in Resource IDs
DATAGOV_RESOURCES = {
    "hospitals": "hospital-directory-resource-id",
    "diseases": "disease-outbreak-resource-id",
    "medicines": "medicine-availability-resource-id",
    "doctors": "doctor-directory-resource-id"
}
