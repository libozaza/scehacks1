not#!/bin/bash

# What Did I Just Do? - Setup Script
echo "🚀 Setting up What Did I Just Do? - Personal Work Activity Tracker"
echo "=================================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.8+ and try again."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed. Please install Node.js 18+ and try again."
    exit 1
fi

echo "✅ Python and Node.js are installed"

# Backend setup
echo ""
echo "🔧 Setting up backend..."
cd backend

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp env.example .env
    echo "⚠️  Please edit backend/.env and add your GEMINI_API_KEY"
fi

cd ..

# Frontend setup
echo ""
echo "🎨 Setting up frontend..."
cd frontend

# Install dependencies
echo "Installing Node.js dependencies..."
npm install

cd ..

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Get a Google Gemini API key from: https://makersuite.google.com/app/apikey"
echo "2. Edit backend/.env and add your GEMINI_API_KEY"
echo "3. Start the backend:"
echo "   cd backend && source venv/bin/activate && python main.py"
echo "4. Start the frontend (in a new terminal):"
echo "   cd frontend && npm run dev"
echo "5. Install the Chrome extension:"
echo "   - Open chrome://extensions/"
echo "   - Enable Developer mode"
echo "   - Click 'Load unpacked' and select the chrome-extension/ folder"
echo ""
echo "🌐 Then visit http://localhost:3000 to start tracking your productivity!"
echo ""
echo "📚 For detailed instructions, see the README.md files in each directory."
