# Dockerfile for GeoNews AI Backend
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies with optimization
RUN pip install --no-cache-dir -r requirements.txt && \
    find /usr/local/lib/python3.11/site-packages -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true && \
    find /usr/local/lib/python3.11/site-packages -type f -name "*.pyc" -delete

# Download CAMeL Tools NER model
# This is required for Arabic NER functionality
RUN python << 'EOF'
import os
import sys

# Create directory for CAMeL tools data
os.makedirs('/root/.camel_tools/data/ner', exist_ok=True)

try:
    from camel_tools.ner import NERecognizer
    print("✅ Loading CAMeL NER model...")
    recognizer = NERecognizer.pretrained()
    print("✅ CAMeL NER model loaded successfully")
except Exception as e:
    print(f"⚠️  Warning: Could not load CAMeL NER model: {e}")
    print("System will use simple NER fallback")
    sys.exit(0)
EOF

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Expose port
EXPOSE 7235

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7235/health || exit 1

# Run the application
CMD uvicorn app.main:app --host 0.0.0.0 --port 7235
