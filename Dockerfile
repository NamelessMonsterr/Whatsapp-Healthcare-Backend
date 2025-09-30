# Multi-stage build for optimized production image
FROM python:3.11-slim as builder

# Set build arguments
ARG APP_USER=healthcarebot
ARG APP_GROUP=healthcarebot
ARG APP_UID=1000
ARG APP_GID=1000

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim as production

# Set build arguments
ARG APP_USER=healthcarebot
ARG APP_GROUP=healthcarebot
ARG APP_UID=1000
ARG APP_GID=1000

# Create non-root user
RUN groupadd -g $APP_GID $APP_GROUP && \
    useradd -u $APP_UID -g $APP_GID -m -s /bin/bash $APP_USER

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/data/models /app/data/backups /app/temp && \
    chown -R $APP_USER:$APP_GROUP /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=$APP_USER:$APP_GROUP . .

# Switch to non-root user
USER $APP_USER

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health', timeout=5)"

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000", "--workers", "4", "--log-level", "info"]
