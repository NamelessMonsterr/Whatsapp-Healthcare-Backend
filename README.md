# 🏥 Healthcare WhatsApp Chatbot

A sophisticated AI-powered WhatsApp chatbot providing instant healthcare information, symptom analysis, and medical guidance in multiple languages.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![WhatsApp](https://img.shields.io/badge/WhatsApp-Business_API-green)

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Endpoints](#-api-endpoints)
- [Project Structure](#-project-structure)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### Core Capabilities
- **🤖 AI-Powered Health Analysis**: Advanced symptom checking and health query processing
- **🌐 Multi-Language Support**: Supports Hindi, English, and regional languages
- **⚡ Real-Time Response**: Instant medical information and guidance
- **📊 Symptom Analysis**: Intelligent symptom evaluation and recommendations
- **🏥 Emergency Detection**: Automatic detection and escalation of emergency situations
- **📱 WhatsApp Integration**: Seamless integration with WhatsApp Business API

### Healthcare Features
- **Symptom Checker**: Analyze symptoms and provide potential conditions
- **Medicine Information**: Detailed information about medications and usage
- **Emergency Guidance**: First-aid instructions and emergency protocols
- **Hospital Locator**: Find nearby hospitals and healthcare facilities
- **Health Tips**: Preventive care and wellness recommendations
- **Vaccination Information**: Immunization schedules and vaccine details

### Technical Features
- **🔐 Secure Data Handling**: HIPAA-compliant data storage and processing
- **📈 Analytics Dashboard**: Track usage patterns and health trends
- **🔄 Session Management**: Contextual conversation handling
- **📝 Logging System**: Comprehensive logging for debugging and monitoring
- **⚡ Caching**: Efficient response caching for improved performance
- **🛡️ Rate Limiting**: Protection against spam and abuse

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│                 │     │                  │     │                 │
│  WhatsApp User  │────▶│  WhatsApp Cloud  │────▶│  FastAPI Server │
│                 │     │       API        │     │                 │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                           │
                                ┌──────────────────────────┼──────────────────────────┐
                                │                          │                          │
                        ┌───────▼────────┐     ┌──────────▼─────────┐     ┌──────────▼────────┐
                        │                │     │                    │     │                   │
                        │  ML Models     │     │  Database          │     │  External APIs    │
                        │  - NLP         │     │  - SQLite/MySQL    │     │  - Hospital API   │
                        │  - Symptom AI  │     │  - User Sessions   │     │  - Medicine DB    │
                        │                │     │                    │     │                   │
                        └────────────────┘     └────────────────────┘     └───────────────────┘
```

## 📋 Prerequisites

- Python 3.8 or higher
- WhatsApp Business Account
- Meta Developer Account
- Facebook App with WhatsApp Business API access
- SSL Certificate (for production)
- 4GB RAM minimum
- 10GB storage space

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/healthcare-whatsapp-bot.git
cd healthcare-whatsapp-bot
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Download ML Models

```bash
python scripts/download_models.py
```

## ⚙️ Configuration

### 1. Environment Variables

Create a `.env` file in the root directory:

```env
# WhatsApp Configuration
WHATSAPP_ACCESS_TOKEN=your_access_token_here
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_VERIFY_TOKEN=your_verify_token
WHATSAPP_BUSINESS_ACCOUNT_ID=your_business_account_id

# Database Configuration
DATABASE_URL=sqlite:///./healthcare.db
# For PostgreSQL: postgresql://user:password@localhost/dbname

# Security
SECRET_KEY=your-secret-key-here
ADMIN_PHONE_NUMBERS=911234567890,919876543210
ENCRYPTION_KEY=your-encryption-key

# API Keys (Optional)
GOOGLE_MAPS_API_KEY=your_google_maps_key
OPENAI_API_KEY=your_openai_key
TRANSLATION_API_KEY=your_translation_key

# App Settings
DEBUG=True
LOG_LEVEL=INFO
MAX_CONVERSATION_HISTORY=20
SESSION_TIMEOUT_MINUTES=30
RATE_LIMIT_PER_MINUTE=30

# ML Model Settings
USE_GPU=False
MODEL_CACHE_DIR=./models
CONFIDENCE_THRESHOLD=0.7

# External APIs
HOSPITAL_API_URL=https://api.example.com/hospitals
MEDICINE_DB_API_URL=https://api.example.com/medicines
GOVERNMENT_HEALTH_API=https://api.data.gov.in/health
```

### 2. WhatsApp Setup

#### Get WhatsApp Access Token:

1. Go to [Meta for Developers](https://developers.facebook.com)
2. Create or select your app
3. Add WhatsApp product to your app
4. Navigate to WhatsApp → API Setup
5. Generate a permanent access token

#### Configure Webhook:

1. In your Meta app dashboard, go to WhatsApp → Configuration
2. Set Webhook URL: `https://yourdomain.com/webhook`
3. Set Verify Token: Same as `WHATSAPP_VERIFY_TOKEN` in `.env`
4. Subscribe to webhook fields:
   - `messages`
   - `messaging_postbacks`
   - `messaging_optins`
   - `message_delivery`

### 3. Database Setup

```bash
# Initialize database
python scripts/init_db.py

# Run migrations (if using Alembic)
alembic upgrade head
```

## 📱 Usage

### Starting the Server

#### Development Mode:

```bash
uvicorn app.main:app --reload --port 5000 --host 0.0.0.0
```

#### Production Mode:

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:5000
```

### Docker Deployment:

```bash
# Build image
docker build -t healthcare-bot .

# Run container
docker run -d \
  --name healthcare-bot \
  -p 5000:5000 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  healthcare-bot
```

### Testing the Bot

1. **Send a WhatsApp message** to your configured business number
2. **Try these commands:**
   - "Hi" - Get started
   - "I have a headache" - Symptom analysis
   - "Tell me about paracetamol" - Medicine information
   - "Emergency" - Emergency assistance
   - "Nearby hospitals" - Location-based services

🚨 Alert System
Emergency Detection & SMS Alerts
The bot includes an advanced emergency detection system that automatically sends SMS alerts to administrators when critical situations are detected.

Testing Twilio Integration

# Test Twilio SMS functionality
python test_twilio_integration.py
test_twilio_integration.py:

# Complete Alert System Script
send_alert_fixed_complete.py:

## 🔌 API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/webhook` | GET | WhatsApp webhook verification |
| `/webhook` | POST | Receive WhatsApp messages |
| `/api/health` | GET | API health status |
| `/api/stats` | GET | Bot statistics |

### Admin Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/admin/dashboard` | GET | Admin dashboard |
| `/admin/users` | GET | List all users |
| `/admin/conversations` | GET | View conversations |
| `/admin/analytics` | GET | Analytics data |
| `/admin/broadcast` | POST | Send broadcast message |

### API Documentation

- Swagger UI: `http://localhost:5000/docs`
- ReDoc: `http://localhost:5000/redoc`

## 📁 Project Structure

```
healthcare-whatsapp-bot/
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration settings
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── endpoints/
│   │   │   ├── webhook.py     # WhatsApp webhook
│   │   │   ├── health.py      # Health endpoints
│   │   │   └── admin.py       # Admin endpoints
│   │   └── middleware.py      # Custom middleware
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── database.py        # Database connection
│   │   ├── security.py        # Security utilities
│   │   └── logging.py         # Logging configuration
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py           # User model
│   │   ├── conversation.py   # Conversation model
│   │   └── health_data.py    # Health data models
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── whatsapp.py       # WhatsApp service
│   │   ├── message_processor.py # Message processing
│   │   ├── health_analyzer.py   # Health analysis
│   │   └── emergency_handler.py # Emergency handling
│   │
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── symptom_checker.py   # Symptom analysis
│   │   ├── nlp_processor.py     # NLP processing
│   │   └── models/              # ML model files
│   │
│   └── utils/
│       ├── __init__.py
│       ├── validators.py        # Input validation
│       ├── formatters.py        # Response formatting
│       └── helpers.py           # Helper functions
│
├── data/
│   ├── symptoms.json            # Symptom database
│   ├── medicines.json           # Medicine database
│   ├── hospitals.json           # Hospital data
│   └── responses.json           # Response templates
│
├── scripts/
│   ├── init_db.py              # Database initialization
│   ├── download_models.py      # Model downloader
│   └── test_webhook.py         # Webhook tester
│
├── tests/
│   ├── __init__.py
│   ├── test_api.py            # API tests
│   ├── test_ml.py             # ML model tests
│   └── test_services.py       # Service tests
│
├── docs/
│   ├── API.md                 # API documentation
│   ├── DEPLOYMENT.md          # Deployment guide
│   └── TROUBLESHOOTING.md     # Troubleshooting guide
│
├── .env.example               # Environment variables example
├── .gitignore                # Git ignore file
├── requirements.txt          # Python dependencies
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose file
└── README.md               # This file
```

## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_api.py

# Run with verbose output
pytest -v
```

### Test WhatsApp Integration

```bash
python scripts/test_webhook.py
```

## 🚀 Deployment

### Using Docker

```bash
# Build and run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Using Kubernetes

```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: healthcare-bot
spec:
  replicas: 3
  selector:
    matchLabels:
      app: healthcare-bot
  template:
    metadata:
      labels:
        app: healthcare-bot
    spec:
      containers:
      - name: healthcare-bot
        image: healthcare-bot:latest
        ports:
        - containerPort: 5000
        envFrom:
        - secretRef:
            name: healthcare-bot-secrets
```

### Cloud Deployment Options

#### AWS EC2
```bash
# Install dependencies
sudo apt update
sudo apt install python3-pip nginx supervisor

# Clone and setup
git clone <repo>
cd healthcare-whatsapp-bot
pip3 install -r requirements.txt

# Configure nginx and supervisor
sudo cp deployment/nginx.conf /etc/nginx/sites-available/healthcare-bot
sudo cp deployment/supervisor.conf /etc/supervisor/conf.d/healthcare-bot.conf
```

#### Heroku
```bash
# Create Heroku app
heroku create healthcare-whatsapp-bot

# Set environment variables
heroku config:set WHATSAPP_ACCESS_TOKEN=your_token

# Deploy
git push heroku main
```

#### Google Cloud Run
```bash
# Build and push image
gcloud builds submit --tag gcr.io/PROJECT_ID/healthcare-bot

# Deploy
gcloud run deploy --image gcr.io/PROJECT_ID/healthcare-bot --platform managed
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Token Expired Error
```
Error: Session has expired
Solution: Generate new access token from Meta Developer Dashboard
```

#### 2. Webhook Verification Failed
```
Error: Webhook verification failed
Solution: Check WHATSAPP_VERIFY_TOKEN matches dashboard configuration
```

#### 3. Database Connection Error
```
Error: Cannot connect to database
Solution: Check DATABASE_URL and ensure database server is running
```

#### 4. Model Loading Error
```
Error: Model not found
Solution: Run python scripts/download_models.py
```

### Debug Mode

Enable detailed logging:
```python
# In .env
DEBUG=True
LOG_LEVEL=DEBUG
```

### Health Check

```bash
curl http://localhost:5000/api/health
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md).

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


## 🙏 Acknowledgments

- Meta for WhatsApp Business API
- FastAPI team for the excellent framework
- Open-source ML community
- Healthcare data providers


## 🔄 Version History

- **v1.0.0** (2024-01-15): Initial release
- **v1.1.0** (2024-02-01): Added multi-language support
- **v1.2.0** (2024-03-01): Enhanced symptom checker
- **v1.3.0** (2024-04-01): Added emergency detection

---

**Made with ❤️ for better healthcare accessibility**

