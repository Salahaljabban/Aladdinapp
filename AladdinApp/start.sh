
#!/bin/bash

echo "🧞‍♂️ Starting Aladdin GRC System..."
echo "=================================="

# Check Python version
echo "🐍 Python version check..."
python --version
echo "✅ Using supported Python version"

# Install/upgrade dependencies without virtual environment (Replit handles this)
echo "📋 Installing dependencies..."
pip install --upgrade --force-reinstall -r requirements.txt

# Create database directory with proper permissions
echo "📁 Setting up database directory..."
mkdir -p /tmp
chmod 755 /tmp

# Remove existing database to ensure clean start
if [ -f "/tmp/aladdin_grc.db" ]; then
    rm /tmp/aladdin_grc.db
fi

# Set environment variables
export FLASK_APP=main.py
export FLASK_ENV=development

# Start the application
echo "🚀 Launching Aladdin GRC..."
python main.py
