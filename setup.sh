#!/bin/bash

# Hotel Risk Monitoring Agent - Setup Script

echo "🏨 Hotel Risk Monitoring Agent - Setup"
echo "========================================"
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
echo ""
echo "Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt
echo "✓ Dependencies installed"

# Create .env file
echo ""
echo "Setting up configuration..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ Created .env file (edit with your API keys)"
else
    echo "✓ .env already exists"
fi

# Create logs directory
mkdir -p logs
echo "✓ Created logs directory"

# Create data directory
mkdir -p data
echo "✓ Created data directory"

echo ""
echo "========================================"
echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your API keys:"
echo "   • NEWS_API_KEY from https://newsapi.org"
echo "   • Gmail SMTP credentials"
echo "   • Email recipient list"
echo ""
echo "2. Add your hotels to config/hotels.json"
echo ""
echo "3. Run once to test:"
echo "   python -m src.scheduler --mode once"
echo ""
echo "4. Or start daily scheduler:"
echo "   python -m src.scheduler --mode daemon --time 09:00"
echo ""
