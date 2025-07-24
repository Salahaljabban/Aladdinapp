
#!/bin/bash

echo "🧞‍♂️ Starting Aladdin GRC System..."
echo "=================================="

# Install/upgrade dependencies without virtual environment (Replit handles this)
echo "📋 Installing dependencies..."
pip install -r requirements.txt

# Create instance directory with proper permissions
echo "📁 Setting up database directory..."
mkdir -p instance
chmod 755 instance

# Remove existing database to ensure clean start
if [ -f "instance/aladdin_grc.db" ]; then
    rm instance/aladdin_grc.db
fi

# Set environment variables
export FLASK_APP=main.py
export FLASK_ENV=development

# Start the application
echo "🚀 Launching Aladdin GRC..."
python main.py
