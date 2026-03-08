#!/bin/bash
# Entrypoint script for Docker deployment
# Downloads models and starts the application

set -e

echo "🚀 Starting application setup..."

# Try to download CAMeL models (optional, won't fail if it doesn't work)
echo "📥 Attempting to download CAMeL models..."
python scripts/download_camel_models.py || echo "⚠️  CAMeL models not available, will use simple NER"

echo "✅ Setup complete, starting application..."

# Start the application
exec "$@"
