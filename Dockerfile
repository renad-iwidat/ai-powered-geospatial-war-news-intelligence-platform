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

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download CAMeL Tools data using camel_data CLI
# This downloads the AraBERT NER model (~500MB)
RUN camel_data -i ner-arabert

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser

# Copy CAMeL Tools data to appuser home directory
RUN if [ -d /root/.camel_tools ]; then \
        cp -r /root/.camel_tools /home/appuser/.camel_tools && \
        chown -R appuser:appuser /home/appuser/.camel_tools; \
    else \
        echo "WARNING: CAMeL Tools data not found in /root/.camel_tools"; \
        ls -la /root/; \
    fi && \
    chown -R appuser:appuser /app

USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
