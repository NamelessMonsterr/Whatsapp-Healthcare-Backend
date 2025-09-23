# WhatsApp API Configuration
WHATSAPP_ACCESS_TOKEN = "EAAJeAB9cxNMBPUx2wZA5qVWmbZBcZAHduzywZBnJW8V7ZCwqTRTsgZCsft5OtgUjJnMPxtZAej4VZBDkLGfUFT8vFpJZCvuvrh8iB2LhxIXWs7Nom8eyD4TZCv0nV7hgWERtjm48YQ93IvibxWzZCSbXLgMuZCSySDLsxvVzOiQqq9lxtmcjWYjhflURbJkE9JThtgngG5DAFZCoKZAPvxqlfZBOiwz536vCOn1c0haXoEn5pa9JoIrJgZDZD"
WHATSAPP_PHONE_NUMBER_ID = "742954942242352"
WHATSAPP_API_VERSION = "v18.0"
WHATSAPP_API_URL = "https://graph.facebook.com/v18.0"

# Example usage in your application:
import requests

def send_whatsapp_message(to_number: str, message: str):
    url = f"{WHATSAPP_API_URL}/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "messaging_product": "whatsapp", 
        "to": to_number,
        "type": "text",
        "text": {"body": message}
    }
    
    response = requests.post(url, headers=headers, json=data)
    return response.status_code == 200, response.json()