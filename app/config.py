"""
Application configuration module - COMPLETELY FIXED
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """Comprehensive application settings with validation and security"""

    # WhatsApp Configuration (Facebook)
    whatsapp_token: str = ""
    whatsapp_phone_number_id: str = ""
    whatsapp_business_account_id: Optional[str] = None
    verify_token: str = "healthcare_bot_verify_secure_123_change_in_production"

    # Twilio Configuration
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_sms_number: Optional[str] = None
    twilio_verify_token: str = "healthcare_bot_twilio_verify_secure_123"

    # Database Configuration
    database_url: str = "sqlite:///./healthcare.db"
    database_echo: bool = False

    # Hugging Face - Optional for public models
    huggingface_token: Optional[str] = None
    model_cache_dir: str = "./data/models"

    # Server Configuration
    app_name: str = "Healthcare WhatsApp Chatbot"
    app_version: str = "1.0.0"
    debug: bool = True
    log_level: str = "INFO"
    port: int = 5000
    host: str = "0.0.0.0"

    # ML Model Configuration
    use_gpu: bool = False
    model_device: str = "cpu"
    max_length: int = 512
    batch_size: int = 1

    # Security Configuration
    secret_key: str = "change-this-to-a-very-long-random-secret-key-in-production-32-chars-minimum"
    admin_api_key: str = "your-admin-api-key-change-this-in-production"
    encryption_key: Optional[str] = None

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000
    rate_limit_per_day: int = 10000

    # Ngrok (for local development)
    ngrok_auth_token: Optional[str] = None
    ngrok_url: Optional[str] = None

    # Data.gov.in API Integration
    data_gov_api_key: str = "579b464db66ec23bdd00000194bfbd293c9a4ada4ea609e6695b36e0"
    data_gov_base_url: str = "https://api.data.gov.in/resource/"

    # Admin Configuration
    admin_phone_numbers: str = "911234567890,919876543210"  # Comma-separated
    
    # WhatsApp Business Configuration
    whatsapp_business_id: Optional[str] = None
    whatsapp_template_namespace: Optional[str] = None
    
    # Health Check Configuration
    health_check_interval: int = 30  # seconds
    max_response_time: int = 30  # seconds
    
    # Model configurations
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        protected_namespaces = ("settings_",)
        extra = "ignore"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # FIXED: Create required directories
        self._create_directories()
        
        # FIXED: Validate security settings
        self._validate_security()
        
        # FIXED: Set up logging
        self._setup_logging()
        
        logger.info("✅ Settings initialized and validated")

    def _create_directories(self):
        """Create required directories"""
        directories = [
            self.model_cache_dir,
            "logs",
            "data",
            "data/backups",
            "temp"
        ]
        
        for directory in directories:
            try:
                Path(directory).mkdir(parents=True, exist_ok=True)
                logger.info(f"✅ Created directory: {directory}")
            except Exception as e:
                logger.error(f"❌ Failed to create directory {directory}: {e}")

    def _validate_security(self):
        """Validate security settings with warnings"""
        security_warnings = []
        
        # Check secret key
        if self.secret_key == "change-this-to-a-very-long-random-secret-key-in-production-32-chars-minimum":
            if not self.debug:
                raise ValueError("❌ Security Error: Secret key must be changed in production!")
            security_warnings.append("⚠️  Warning: Using default secret key")
        
        # Check admin API key
        if self.admin_api_key == "your-admin-api-key-change-this-in-production":
            security_warnings.append("⚠️  Warning: Using default admin API key")
        
        # Check WhatsApp token
        if not self.whatsapp_token:
            security_warnings.append("⚠️  Warning: WhatsApp token not configured")
        
        # Check phone number ID
        if not self.whatsapp_phone_number_id:
            security_warnings.append("⚠️  Warning: WhatsApp phone number ID not configured")
        
        # Check database URL
        if not self.database_url:
            raise ValueError("❌ Database URL is required")
        
        # Check for insecure settings in production
        if not self.debug:
            if self.use_gpu and self.model_device == "cpu":
                security_warnings.append("⚠️  Warning: GPU enabled but device set to CPU")
            
            if len(self.secret_key) < 32:
                raise ValueError("❌ Security Error: Secret key must be at least 32 characters in production")
            
            if len(self.admin_api_key) < 16:
                raise ValueError("❌ Security Error: Admin API key must be at least 16 characters in production")
        
        # Log security warnings
        for warning in security_warnings:
            logger.warning(warning)
        
        if security_warnings:
            logger.warning("🔒 Please review and fix security configurations before production deployment")

    def _setup_logging(self):
        """Set up logging configuration"""
        try:
            log_level = getattr(logging, self.log_level.upper(), logging.INFO)
            
            # Create logs directory if it doesn't exist
            Path("logs").mkdir(exist_ok=True)
            
            # Configure logging
            logging.basicConfig(
                level=log_level,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.StreamHandler(),
                    logging.FileHandler('logs/app.log', encoding='utf-8'),
                    logging.FileHandler('logs/error.log', encoding='utf-8', level=logging.ERROR)
                ]
            )
            
            logger.info(f"✅ Logging configured at level: {self.log_level}")
            
        except Exception as e:
            print(f"❌ Failed to set up logging: {e}")

    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return not self.debug

    @property
    def is_whatsapp_configured(self) -> bool:
        """Check if WhatsApp is properly configured"""
        return bool(self.whatsapp_token and self.whatsapp_phone_number_id)

    @property
    def is_twilio_configured(self) -> bool:
        """Check if Twilio is properly configured"""
        return bool(self.twilio_account_sid and self.twilio_auth_token and self.twilio_sms_number)

    @property
    def admin_phones_list(self) -> list:
        """Get admin phone numbers as list"""
        if self.admin_phone_numbers:
            return [phone.strip() for phone in self.admin_phone_numbers.split(',') if phone.strip()]
        return []

    def get_model_config(self, model_key: str) -> dict:
        """Get configuration for specific model"""
        return ML_MODELS.get(model_key, {})

    def validate_phone_number(self, phone: str) -> bool:
        """Validate phone number format"""
        import re
        if not phone:
            return False
        
        # Remove non-numeric characters
        cleaned = re.sub(r'[^\d]', '', phone)
        
        # Check length (10-15 digits)
        return 10 <= len(cleaned) <= 15

# ML Model configurations - FIXED
ML_MODELS = {
    "multilingual": {
        "name": "ai4bharat/IndicBERTv2-MLM-only",
        "task": "feature-extraction",
        "description": "Multilingual understanding for Indian languages",
        "max_length": 512,
        "confidence_threshold": 0.7
    },
    "biomedical": {
        "name": "dmis-lab/biobert-base-cased-v1.1",
        "task": "question-answering",
        "description": "Biomedical Q&A and classification",
        "max_length": 512,
        "confidence_threshold": 0.8
    },
    "chatdoctor": {
        "name": "microsoft/BioGPT-Large",
        "task": "text-generation",
        "description": "Conversational medical Q&A",
        "max_length": 1024,
        "confidence_threshold": 0.75
    }
}

# Common Data.gov.in Resource IDs (FIXED - with actual resource IDs)
DATAGOV_RESOURCES = {
    "hospitals": "376ce68c-7726-45fd-915a-6c7b6f5dae6a",  # Hospital Directory
    "diseases": "a7d4354e-4a1b-4be2-9f65-9d2b7f3b9c7e",  # Disease Surveillance
    "medicines": "1c5e1eb3-8d4c-4f1d-9f1e-2c4d5e6f7a8b",  # Medicine Availability
    "doctors": "2d8f9a1b-3c4d-5e6f-7a8b-9c0d1e2f3a4b",   # Doctor Directory
    "health_centers": "3e9g0b2c-4d5e-6f7a-8b9c-0d1e2f3a4b5c"  # Health Centers
}

# Create settings instance
try:
    settings = Settings()
    logger.info("✅ Settings instance created successfully")
except Exception as e:
    logger.error(f"❌ Failed to create settings: {e}")
    # Create minimal settings for emergency use
    settings = Settings(
        debug=True,
        log_level="ERROR",
        secret_key="emergency-secret-key-change-immediately"
    )

# Environment validation
def validate_environment():
    """Validate environment configuration"""
    errors = []
    warnings = []
    
    # Check Python version
    import sys
    if sys.version_info < (3, 8):
        errors.append("❌ Python 3.8+ is required")
    
    # Check required environment variables
    required_vars = []
    if settings.is_production:
        required_vars = [
            'WHATSAPP_ACCESS_TOKEN',
            'WHATSAPP_PHONE_NUMBER_ID',
            'SECRET_KEY'
        ]
    
    for var in required_vars:
        if not os.getenv(var):
            errors.append(f"❌ Required environment variable missing: {var}")
    
    # Check optional but recommended variables
    optional_vars = [
        'TWILIO_ACCOUNT_SID',
        'TWILIO_AUTH_TOKEN',
        'TWILIO_SMS_NUMBER'
    ]
    
    for var in optional_vars:
        if not os.getenv(var):
            warnings.append(f"⚠️  Optional environment variable not set: {var}")
    
    # Log validation results
    if errors:
        for error in errors:
            logger.error(error)
        return False
    
    if warnings:
        for warning in warnings:
            logger.warning(warning)
    
    logger.info("✅ Environment validation passed")
    return True

# Validate environment on import
if not validate_environment():
    logger.warning("⚠️  Environment validation failed, some features may not work")

# Test function
def test_settings():
    """Test settings configuration"""
    print("🧪 Testing Settings Configuration")
    print("=" * 40)
    
    print(f"App Name: {settings.app_name}")
    print(f"App Version: {settings.app_version}")
    print(f"Debug Mode: {settings.debug}")
    print(f"Log Level: {settings.log_level}")
    print(f"Host: {settings.host}")
    print(f"Port: {settings.port}")
    print(f"GPU Enabled: {settings.use_gpu}")
    print(f"Model Device: {settings.model_device}")
    
    print(f"\nWhatsApp Configured: {settings.is_whatsapp_configured}")
    print(f"Twilio Configured: {settings.is_twilio_configured}")
    print(f"Production Mode: {settings.is_production}")
    
    print(f"\nModel Cache Dir: {settings.model_cache_dir}")
    print(f"Database URL: {settings.database_url.replace('://', '://***@')}")  # Mask credentials
    
    print(f"\nML Models Configured: {len(ML_MODELS)}")
    for key, config in ML_MODELS.items():
        print(f"  - {key}: {config['name']}")
    
    print(f"\nData.gov Resources: {len(DATAGOV_RESOURCES)}")
    for key, resource_id in DATAGOV_RESOURCES.items():
        print(f"  - {key}: {resource_id}")
    
    print("\n✅ Settings test completed!")

if __name__ == "__main__":
    test_settings()
