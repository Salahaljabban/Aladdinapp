
#!/bin/bash

echo "🧞‍♂️ Starting Aladdin GRC System..."
echo "=================================="

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "📦 Setting up Python environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate 2>/dev/null || echo "⚠️  Running without virtual environment"

# Install/upgrade dependencies
echo "📋 Installing dependencies..."
pip install -r requirements.txt

# Create instance directory if it doesn't exist
mkdir -p instance

# Set environment variables
export FLASK_APP=main.py
export FLASK_ENV=development

# Start the application
echo "🚀 Launching Aladdin GRC..."
python main.py
