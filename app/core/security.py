"""
Security utilities - COMPLETELY FIXED VERSION
"""
import secrets
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Optional
import logging
import re
import uuid
from app.config import settings

logger = logging.getLogger(__name__)

# FIXED: Add missing admin_api_key to settings validation
def validate_admin_api_key(api_key: str) -> bool:
    """
    Validate admin API key with proper security checks

    Args:
        api_key: The API key to validate

    Returns:
        True if valid, False otherwise
    """
    if not api_key:
        return False
    
    # FIXED: Get admin API key from settings with fallback
    admin_key = getattr(settings, 'admin_api_key', 'your-admin-api-key-change-this-in-production')
    
    # FIXED: Use proper constant-time comparison to prevent timing attacks
    return secrets.compare_digest(api_key, admin_key)

def generate_secure_token(length: int = 32) -> str:
    """
    Generate a cryptographically secure random token

    Args:
        length: Length of the token in bytes

    Returns:
        Secure random token as URL-safe string
    """
    return secrets.token_urlsafe(length)

def hash_sensitive_data(data: str, salt: Optional[str] = None) -> str:
    """
    Hash sensitive data with salt for storage

    Args:
        data: Data to hash
        salt: Optional salt, generated if not provided

    Returns:
        Hashed data as hex string
    """
    if not data:
        return ""
    
    if salt is None:
        salt = secrets.token_hex(16)

    # FIXED: Use SHA-256 with proper salt handling
    try:
        hashed = hashlib.sha256((data + salt).encode('utf-8')).hexdigest()
        return f"{salt}${hashed}"
    except Exception as e:
        logger.error(f"Error hashing data: {e}")
        return ""

def verify_hashed_data(data: str, hashed: str) -> bool:
    """
    Verify data against hashed value

    Args:
        data: Original data to verify
        hashed: Hashed value with salt

    Returns:
        True if data matches hash
    """
    if not data or not hashed:
        return False
    
    try:
        parts = hashed.split("$", 1)
        if len(parts) != 2:
            return False
        
        salt, hash_value = parts
        expected_hash = hash_sensitive_data(data, salt)
        return secrets.compare_digest(expected_hash, hashed)
    except (ValueError, AttributeError, Exception) as e:
        logger.error(f"Error verifying hash: {e}")
        return False

def sanitize_phone_number(phone: str) -> str:
    """
    Sanitize and validate phone number

    Args:
        phone: Raw phone number

    Returns:
        Sanitized phone number or empty string if invalid
    """
    if not phone:
        return ""

    # FIXED: Remove all non-numeric characters
    cleaned = re.sub(r'[^\d]', '', str(phone))
    
    # FIXED: Basic validation - should be 10-15 digits
    if len(cleaned) < 10 or len(cleaned) > 15:
        return ""
    
    # FIXED: Handle different country codes properly
    if len(cleaned) == 10:
        # Assume Indian number
        cleaned = "91" + cleaned
    elif len(cleaned) == 12 and cleaned.startswith("91"):
        # Already has Indian country code
        pass
    elif len(cleaned) > 12:
        # International number, keep as is
        pass
    
    return cleaned

def validate_whatsapp_phone(phone: str) -> str:
    """
    Validate and format phone number for WhatsApp

    Args:
        phone: Raw phone number

    Returns:
        Formatted phone number or raises ValueError
    """
    if not phone:
        raise ValueError("Phone number is required")
    
    # FIXED: Handle different input formats
    phone_str = str(phone).strip()
    
    # Remove WhatsApp prefix if present
    phone_str = phone_str.replace('whatsapp:', '')
    
    # Remove + prefix if present
    phone_str = phone_str.lstrip('+')
    
    # Sanitize the phone number
    cleaned = sanitize_phone_number(phone_str)
    if not cleaned:
        raise ValueError("Invalid phone number format")
    
    # FIXED: Additional validation for WhatsApp
    if len(cleaned) < 10 or len(cleaned) > 15:
        raise ValueError("Phone number must be between 10 and 15 digits")
    
    # Check for obvious invalid patterns
    if all(c == '0' for c in cleaned):
        raise ValueError("Phone number cannot be all zeros")
    
    if cleaned.startswith('0') and len(cleaned) > 10:
        raise ValueError("International numbers should not start with 0")
    
    return cleaned

def is_safe_message_content(content: str) -> tuple[bool, str]:
    """
    Check if message content is safe (comprehensive content filtering)

    Args:
        content: Message content to check

    Returns:
        Tuple of (is_safe, reason_if_not_safe)
    """
    if not content:
        return True, ""
    
    # FIXED: Check message length with proper limit
    if len(content) > 4096:  # WhatsApp's actual message limit
        return False, "Message too long (max 4096 characters)"
    
    # FIXED: Comprehensive dangerous pattern detection
    dangerous_patterns = [
        # Script injection
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'vbscript:',
        r'onload\s*=',
        r'onerror\s*=',
        r'onclick\s*=',
        r'onmouseover\s*=',
        
        # Data URLs
        r'data:text/html',
        r'data:application/javascript',
        
        # Template injection
        r'\$\{.*?\}',
        r'\{\{.*?\}\}',
        
        # SQL injection patterns
        r"(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b.*\b(from|where|and|or)\b|--|#|/\*|\*/)",
        
        # Command injection
        r'[`$].*?(rm|sudo|cat|echo|wget|curl|python|bash|sh)\s',
        
        # Path traversal
        r'\.\./|\.\.\\',
        
        # Null bytes
        r'\x00',
        
        # Excessive special characters
        r'[!@#$%^&*()]{10,}',
    ]
    
    content_lower = content.lower()
    for pattern in dangerous_patterns:
        if re.search(pattern, content_lower, re.IGNORECASE):
            logger.warning(f"Potentially dangerous content detected: {pattern}")
            return False, f"Potentially dangerous content detected"
    
    # FIXED: Check for excessive repetition (spam indicator)
    words = content.split()
    if len(words) > 10:
        word_counts = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        # If any word appears too many times, it's likely spam
        for word, count in word_counts.items():
            if count > len(words) * 0.3:  # Word appears in more than 30% of content
                return False, "Excessive repetition detected"
    
    return True, ""

def generate_rate_limit_key(identifier: str, window: int = 60) -> str:
    """
    Generate rate limit key with time window

    Args:
        identifier: User identifier (phone, IP, etc.)
        window: Time window in seconds

    Returns:
        Rate limit key
    """
    if not identifier:
        return ""
    
    # FIXED: Use current time window
    current_window = int(datetime.utcnow().timestamp() / window)
    return f"rate_limit:{identifier}:{current_window}"

def validate_alert_type(alert_type: str) -> bool:
    """
    Validate alert type against allowed types

    Args:
        alert_type: Alert type to validate

    Returns:
        True if valid
    """
    allowed_types = {"info", "warning", "emergency", "outbreak", "health_advisory"}
    return alert_type.lower() in allowed_types

def validate_priority(priority: str) -> bool:
    """
    Validate priority level

    Args:
        priority: Priority to validate

    Returns:
        True if valid
    """
    allowed_priorities = {"low", "normal", "high", "critical"}
    return priority.lower() in allowed_priorities

def validate_disease_name(disease: str) -> bool:
    """
    Validate disease name format

    Args:
        disease: Disease name to validate

    Returns:
        True if valid
    """
    if not disease or len(disease) < 2 or len(disease) > 100:
        return False

    # Basic pattern - letters, spaces, numbers, and common punctuation
    pattern = r'^[a-zA-Z0-9\s\-\(\)\.,]+$'
    return bool(re.match(pattern, disease))

def validate_region_name(region: str) -> bool:
    """
    Validate region name format

    Args:
        region: Region name to validate

    Returns:
        True if valid
    """
    if not region or len(region) < 2 or len(region) > 200:
        return False

    # Basic pattern - letters, spaces, numbers, and common punctuation
    pattern = r'^[a-zA-Z0-9\s\-\(\)\.,/]+$'
    return bool(re.match(pattern, region))

def sanitize_input_string(input_str: str, max_length: int = 500) -> str:
    """
    Sanitize input string by removing potentially dangerous characters

    Args:
        input_str: String to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized string
    """
    if not input_str:
        return ""

    # Truncate if too long
    if len(input_str) > max_length:
        input_str = input_str[:max_length]

    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', '%', '$', '#', '@', '!', '*']
    for char in dangerous_chars:
        input_str = input_str.replace(char, '')

    # Remove multiple spaces
    import re
    input_str = re.sub(r'\s+', ' ', input_str).strip()

    return input_str

def create_audit_log(action: str, user_id: str, details: dict = None) -> dict:
    """
    Create audit log entry

    Args:
        action: Action performed
        user_id: User who performed the action
        details: Additional details

    Returns:
        Audit log entry
    """
    return {
        "action": action,
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat(),
        "details": details or {},
        "id": secrets.token_urlsafe(16)
    }

def mask_sensitive_data(data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
    """
    Mask sensitive data for logging

    Args:
        data: Data to mask
        mask_char: Character to use for masking
        visible_chars: Number of characters to keep visible

    Returns:
        Masked data
    """
    if not data:
        return ""

    if len(data) <= visible_chars:
        return mask_char * len(data)

    visible_start = data[:visible_chars // 2]
    visible_end = data[-visible_chars // 2:]
    masked_middle = mask_char * (len(data) - visible_chars)

    return f"{visible_start}{masked_middle}{visible_end}"

# FIXED: Added security headers middleware
def add_security_headers(response):
    """
    Add security headers to response

    Args:
        response: FastAPI response object

    Returns:
        Response with security headers
    """
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # Remove server identification
    response.headers["Server"] = "HealthcareBot"

    return response
