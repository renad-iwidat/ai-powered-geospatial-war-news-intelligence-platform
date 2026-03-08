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
from pathlib import Path

# Create directory for CAMeL tools data
camel_dir = Path('/root/.camel_tools/data/ner')
camel_dir.mkdir(parents=True, exist_ok=True)

print("📥 Downloading CAMeL NER model...")

try:
    # Set environment variable to use the correct cache directory
    os.environ['CAMEL_DATA_DIR'] = '/root/.camel_tools'
    
    from camel_tools.ner import NERecognizer
    
    # Download and cache the model
    recognizer = NERecognizer.pretrained()
    print("✅ CAMeL NER model downloaded and loaded successfully")
    
except Exception as e:
    print(f"❌ Error downloading CAMeL NER model: {e}")
    print("Attempting alternative download method...")
    
    try:
        # Try downloading from Hugging Face directly
        from huggingface_hub import hf_hub_download
        
        model_id = "CAMeL-Lab/bert-base-arabic-camelbert-msa"
        model_path = hf_hub_download(
            repo_id=model_id,
            filename="pytorch_model.bin",
            cache_dir="/root/.camel_tools/data/ner"
        )
        print(f"✅ Model downloaded to: {model_path}")
        
    except Exception as e2:
        print(f"❌ Alternative download also failed: {e2}")
        sys.exit(1)
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
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-7235}
