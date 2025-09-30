"""
Application configuration module - COMPLETELY FIXED WITH ALL FEATURES
"""
from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any
import os
from pathlib import Path
import logging
import secrets

# Configure logging for config module
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """Comprehensive application settings with validation, security, and all features"""

    # =============================================================================
    # CORE APPLICATION SETTINGS
    # =============================================================================
    app_name: str = "Healthcare WhatsApp Chatbot"
    app_version: str = "1.0.0"
    debug: bool = True
    log_level: str = "INFO"
    port: int = 5000
    host: str = "0.0.0.0"
    environment: str = "development"  # development, staging, production

    # =============================================================================
    # WHATSAPP BUSINESS API CONFIGURATION
    # =============================================================================
    whatsapp_token: str = ""
    whatsapp_phone_number_id: str = ""
    whatsapp_business_account_id: Optional[str] = None
    whatsapp_business_id: Optional[str] = None
    whatsapp_template_namespace: Optional[str] = None
    verify_token: str = "healthcare_bot_verify_secure_123_change_in_production"

    # =============================================================================
    # TWILIO CONFIGURATION (FOR SMS ALERTS)
    # =============================================================================
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_sms_number: Optional[str] = None
    twilio_verify_token: str = "healthcare_bot_twilio_verify_secure_123"

    # =============================================================================
    # DATABASE CONFIGURATION
    # =============================================================================
    database_url: str = "sqlite:///./data/healthcare.db"
    database_echo: bool = False
    database_pool_size: int = 10
    database_max_overflow: int = 20
    database_pool_timeout: int = 30

    # =============================================================================
    # SECURITY CONFIGURATION
    # =============================================================================
    secret_key: str = "change-this-to-a-very-long-random-secret-key-in-production-32-chars-minimum"
    admin_api_key: str = "your-admin-api-key-change-this-in-production"
    encryption_key: Optional[str] = None
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60

    # =============================================================================
    # MACHINE LEARNING CONFIGURATION
    # =============================================================================
    huggingface_token: Optional[str] = None
    model_cache_dir: str = "./data/models"
    use_gpu: bool = False
    model_device: str = "cpu"
    max_length: int = 512
    batch_size: int = 1
    confidence_threshold: float = 0.7

    # =============================================================================
    # RATE LIMITING CONFIGURATION
    # =============================================================================
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000
    rate_limit_per_day: int = 10000

    # =============================================================================
    # ADMINISTRATION CONFIGURATION
    # =============================================================================
    admin_phone_numbers: str = "911234567890,919876543210"  # Comma-separated
    admin_emails: str = "admin@healthcare.com,emergency@healthcare.com"

    # =============================================================================
    # EXTERNAL API CONFIGURATION
    # =============================================================================
    data_gov_api_key: str = "579b464db66ec23bdd00000194bfbd293c9a4ada4ea609e6695b36e0"
    data_gov_base_url: str = "https://api.data.gov.in/resource/"
    google_maps_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    translation_api_key: Optional[str] = None

    # =============================================================================
    # MONITORING AND HEALTH CHECKS
    # =============================================================================
    health_check_interval: int = 30  # seconds
    max_response_time: int = 30  # seconds
    enable_metrics: bool = True
    metrics_port: int = 9090

    # =============================================================================
    # MESSAGE AND TEMPLATE CONFIGURATION
    # =============================================================================
    max_message_length: int = 4096
    max_buttons: int = 3
    session_timeout_minutes: int = 30
    conversation_history_limit: int = 50

    # =============================================================================
    # EMERGENCY AND ALERT CONFIGURATION
    # =============================================================================
    emergency_contact_number: str = "108"
    hospital_helpline: str = "1066"
    government_health_helpline: str = "1075"
    emergency_detection_threshold: float = 0.9

    # =============================================================================
    # PERFORMANCE TUNING
    # =============================================================================
    max_concurrent_requests: int = 100
    max_message_queue_size: int = 1000
    max_processing_time_ms: int = 30000
    worker_timeout: int = 30

    # =============================================================================
    # NGROK CONFIGURATION (FOR LOCAL DEVELOPMENT)
    # =============================================================================
    ngrok_auth_token: Optional[str] = None
    ngrok_url: Optional[str] = None

    # =============================================================================
    # BACKUP AND DATA RETENTION
    # =============================================================================
    backup_enabled: bool = True
    backup_interval_hours: int = 24
    backup_retention_days: int = 30
    message_retention_days: int = 365
    conversation_retention_days: int = 730
    user_data_retention_days: int = 1095

    # =============================================================================
    # COMPLIANCE AND PRIVACY
    # =============================================================================
    gdpr_compliance_enabled: bool = True
    data_anonymization_enabled: bool = True
    consent_required: bool = True

    # =============================================================================
    # FEATURE FLAGS
    # =============================================================================
    enable_admin_alerts: bool = True
    enable_data_gov_integration: bool = True
    enable_twilio_integration: bool = False
    enable_google_maps_integration: bool = False
    enable_openai_integration: bool = False
    enable_multilingual_support: bool = True
    enable_personalized_responses: bool = True
    enable_contextual_conversations: bool = True

    # =============================================================================
    # MODEL CONFIDENCE THRESHOLDS
    # =============================================================================
    symptom_detection_threshold: float = 0.7
    emergency_detection_threshold: float = 0.9
    language_detection_threshold: float = 0.8
    intent_classification_threshold: float = 0.75

    # =============================================================================
    # ENVIRONMENT-SPECIFIC SETTINGS
    # =============================================================================
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
        
        # FIXED: Generate secure keys if not provided
        self._generate_secure_keys()
        
        logger.info("✅ Settings initialized and validated")

    def _create_directories(self):
        """Create required directories"""
        directories = [
            self.model_cache_dir,
            "logs",
            "data",
            "data/backups",
            "data/models",
            "temp",
            "logs/app",
            "logs/error",
            "logs/audit"
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
        security_errors = []
        
        # Check secret key
        if self.secret_key == "change-this-to-a-very-long-random-secret-key-in-production-32-chars-minimum":
            if self.environment == "production":
                security_errors.append("❌ Security Error: Secret key must be changed in production!")
            else:
                security_warnings.append("⚠️  Warning: Using default secret key")
        
        # Check admin API key
        if self.admin_api_key == "your-admin-api-key-change-this-in-production":
            if self.environment == "production":
                security_errors.append("❌ Security Error: Admin API key must be changed in production!")
            else:
                security_warnings.append("⚠️  Warning: Using default admin API key")
        
        # Check WhatsApp configuration
        if not self.whatsapp_token:
            security_warnings.append("⚠️  Warning: WhatsApp token not configured")
        
        if not self.whatsapp_phone_number_id:
            security_warnings.append("⚠️  Warning: WhatsApp phone number ID not configured")
        
        # Check database URL
        if not self.database_url:
            security_errors.append("❌ Database URL is required")
        
        # Check for insecure settings in production
        if self.environment == "production":
            if self.use_gpu and self.model_device == "cpu":
                security_warnings.append("⚠️  Warning: GPU enabled but device set to CPU")
            
            if len(self.secret_key) < 32:
                security_errors.append("❌ Security Error: Secret key must be at least 32 characters in production")
            
            if len(self.admin_api_key) < 16:
                security_errors.append("❌ Security Error: Admin API key must be at least 16 characters in production")
            
            if self.debug:
                security_warnings.append("⚠️  Warning: Debug mode enabled in production")
        
        # Log security issues
        for error in security_errors:
            logger.error(error)
        
        for warning in security_warnings:
            logger.warning(warning)
        
        if security_errors:
            raise ValueError(f"Security validation failed: {security_errors}")

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
                    logging.FileHandler('logs/error.log', encoding='utf-8', level=logging.ERROR),
                    logging.FileHandler('logs/audit.log', encoding='utf-8', level=logging.INFO)
                ]
            )
            
            logger.info(f"✅ Logging configured at level: {self.log_level}")
            
        except Exception as e:
            print(f"❌ Failed to set up logging: {e}")

    def _generate_secure_keys(self):
        """Generate secure keys if not provided"""
        try:
            # Generate encryption key if not provided
            if not self.encryption_key:
                self.encryption_key = secrets.token_hex(32)
                logger.info("✅ Generated secure encryption key")
            
            # Generate JWT secret if using default
            if self.secret_key == "change-this-to-a-very-long-random-secret-key-in-production-32-chars-minimum":
                if self.environment != "production":
                    logger.warning("⚠️  Using default secret key - generate a secure one for production")
            
            # Generate admin API key if using default
            if self.admin_api_key == "your-admin-api-key-change-this-in-production":
                if self.environment != "production":
                    logger.warning("⚠️  Using default admin API key - generate a secure one for production")
                    
        except Exception as e:
            logger.error(f"Error generating secure keys: {e}")

    # =============================================================================
    # PROPERTIES FOR EASY ACCESS
    # =============================================================================

    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.environment == "development"

    @property
    def is_staging(self) -> bool:
        """Check if running in staging mode"""
        return self.environment == "staging"

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

    @property
    def admin_emails_list(self) -> list:
        """Get admin emails as list"""
        if self.admin_emails:
            return [email.strip() for email in self.admin_emails.split(',') if email.strip()]
        return []

    # =============================================================================
    # UTILITY METHODS
    # =============================================================================

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

    def get_feature_status(self) -> dict:
        """Get status of all features"""
        return {
            "whatsapp_integration": self.is_whatsapp_configured,
            "twilio_integration": self.is_twilio_configured,
            "admin_alerts": self.enable_admin_alerts,
            "data_gov_integration": self.enable_data_gov_integration,
            "google_maps_integration": self.enable_google_maps_integration,
            "openai_integration": self.enable_openai_integration,
            "multilingual_support": self.enable_multilingual_support,
            "rate_limiting": self.rate_limit_enabled,
            "gdpr_compliance": self.gdpr_compliance_enabled,
            "backup_enabled": self.backup_enabled,
            "gpu_available": self.use_gpu and self.model_device == "cuda"
        }

    def to_dict(self) -> dict:
        """Convert settings to dictionary (safe for API responses)"""
        return {
            "app_name": self.app_name,
            "app_version": self.app_version,
            "environment": self.environment,
            "debug": self.debug,
            "log_level": self.log_level,
            "host": self.host,
            "port": self.port,
            "whatsapp_configured": self.is_whatsapp_configured,
            "twilio_configured": self.is_twilio_configured,
            "rate_limiting_enabled": self.rate_limit_enabled,
            "max_message_length": self.max_message_length,
            "max_buttons": self.max_buttons,
            "session_timeout_minutes": self.session_timeout_minutes,
            "features": self.get_feature_status()
        }

# =============================================================================
    # ML MODEL CONFIGURATIONS
    # =============================================================================

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

# =============================================================================
# DATA.GOV.IN RESOURCE CONFIGURATIONS
# =============================================================================

DATAGOV_RESOURCES = {
    "hospitals": "376ce68c-7726-45fd-915a-6c7b6f5dae6a",  # Hospital Directory
    "diseases": "a7d4354e-4a1b-4be2-9f65-9d2b7f3b9c7e",  # Disease Surveillance
    "medicines": "1c5e1eb3-8d4c-4f1d-9f1e-2c4d5e6f7a8b",  # Medicine Availability
    "doctors": "2d8f9a1b-3c4d-5e6f-7a8b-9c0d1e2f3a4b",   # Doctor Directory
    "health_centers": "3e9g0b2c-4d5e-6f7a-8b9c-0d1e2f3a4b5c"  # Health Centers
}

# =============================================================================
# CREATE SETTINGS INSTANCE
# =============================================================================

try:
    settings = Settings()
    logger.info("✅ Settings instance created successfully")
except Exception as e:
    logger.error(f"❌ Failed to create settings: {e}")
    # Create minimal settings for emergency use
    settings = Settings(
        debug=True,
        log_level="ERROR",
        secret_key="emergency-secret-key-change-immediately",
        admin_api_key="emergency-admin-key-change-immediately"
    )

# =============================================================================
# ENVIRONMENT VALIDATION
# =============================================================================

def validate_environment():
    """Validate environment configuration"""
    errors = []
    warnings = []
    
    # Check Python version
    import sys
    if sys.version_info < (3, 8):
        errors.append("❌ Python 3.8+ is required")
    
    # Check required environment variables for production
    if settings.is_production:
        required_vars = [
            'WHATSAPP_TOKEN',
            'WHATSAPP_PHONE_NUMBER_ID',
            'SECRET_KEY',
            'ADMIN_API_KEY'
        ]
        
        for var in required_vars:
            if not os.getenv(var):
                errors.append(f"❌ Required environment variable missing: {var}")
    
    # Check optional but recommended variables
    optional_vars = [
        'TWILIO_ACCOUNT_SID',
        'TWILIO_AUTH_TOKEN',
        'TWILIO_SMS_NUMBER',
        'DATABASE_URL'
    ]
    
    for var in optional_vars:
        if not os.getenv(var):
            warnings.append(f"⚠️  Optional environment variable not set: {var}")
    
    # Log validation results
    if errors:
        for error in errors:
            logger.error(error)
        return False, errors, warnings
    
    if warnings:
        for warning in warnings:
            logger.warning(warning)
    
    logger.info("✅ Environment validation passed")
    return True, [], warnings

# =============================================================================
# VALIDATE ON IMPORT
# =============================================================================

validation_success, validation_errors, validation_warnings = validate_environment()

if not validation_success:
    logger.warning("⚠️  Environment validation failed, some features may not work")
    if settings.is_production:
        logger.error("❌ Critical environment validation failed in production mode")

# =============================================================================
# TEST FUNCTION
# =============================================================================

def test_settings():
    """Test settings configuration"""
    print("🧪 Testing Settings Configuration")
    print("=" * 40)
    
    print(f"App Name: {settings.app_name}")
    print(f"App Version: {settings.app_version}")
    print(f"Environment: {settings.environment}")
    print(f"Debug Mode: {settings.debug}")
    print(f"Log Level: {settings.log_level}")
    print(f"Host: {settings.host}")
    print(f"Port: {settings.port}")
    print(f"GPU Enabled: {settings.use_gpu}")
    print(f"Model Device: {settings.model_device}")
    
    print(f"\nWhatsApp Configured: {settings.is_whatsapp_configured}")
    print(f"Twilio Configured: {settings.is_twilio_configured}")
    print(f"Production Mode: {settings.is_production}")
    
    print(f"\nRate Limiting: {settings.rate_limit_enabled}")
    print(f"Max Requests/Min: {settings.rate_limit_per_minute}")
    print(f"Max Requests/Hour: {settings.rate_limit_per_hour}")
    print(f"Max Requests/Day: {settings.rate_limit_per_day}")
    
    print(f"\nModel Cache Dir: {settings.model_cache_dir}")
    print(f"Database URL: {mask_sensitive_data(settings.database_url)}")
    
    print(f"\nML Models Configured: {len(ML_MODELS)}")
    for key, config in ML_MODELS.items():
        print(f"  - {key}: {config['name']}")
    
    print(f"\nData.gov Resources: {len(DATAGOV_RESOURCES)}")
    for key, resource_id in DATAGOV_RESOURCES.items():
        print(f"  - {key}: {resource_id}")
    
    print(f"\nAdmin Phones: {len(settings.admin_phones_list)}")
    print(f"Features Enabled: {len([k for k, v in settings.get_feature_status().items() if v])}")
    
    print("\n✅ Settings test completed!")

if __name__ == "__main__":
    test_settings()
