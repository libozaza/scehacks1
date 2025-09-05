#!/bin/bash

# What Did I Just Do? - Setup Script
echo "🚀 Setting up What Did I Just Do? - Personal Work Activity Tracker"
echo "=================================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if Python is installed
if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 is required but not installed. Please install Python 3.8+ and try again.${NC}"
    exit 1
fi

# Check if Node.js is installed
if ! command_exists node; then
    echo -e "${RED}❌ Node.js is required but not installed. Please install Node.js 18+ and try again.${NC}"
    exit 1
fi

# Check if npm is installed
if ! command_exists npm; then
    echo -e "${RED}❌ npm is required but not installed. Please install npm and try again.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python, Node.js, and npm are installed${NC}"

# Backend setup
echo ""
echo -e "${BLUE}🔧 Setting up backend...${NC}"
cd backend

# Remove existing virtual environment if it exists (to avoid issues)
if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Removing existing virtual environment...${NC}"
    rm -rf venv
fi

# Create virtual environment
echo -e "${BLUE}Creating Python virtual environment...${NC}"
python3 -m venv venv

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip first
echo -e "${BLUE}Upgrading pip...${NC}"
pip install --upgrade pip

# Install dependencies
echo -e "${BLUE}Installing Python dependencies...${NC}"
pip install -r requirements.txt

# Verify FastAPI installation
echo -e "${BLUE}Verifying FastAPI installation...${NC}"
if python -c "import fastapi; print('FastAPI version:', fastapi.__version__)" 2>/dev/null; then
    echo -e "${GREEN}✅ FastAPI installed successfully${NC}"
else
    echo -e "${RED}❌ FastAPI installation failed${NC}"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${BLUE}Creating .env file...${NC}"
    if [ -f env.example ]; then
        cp env.example .env
        echo -e "${YELLOW}⚠️  Please edit backend/.env and add your GEMINI_API_KEY${NC}"
    else
        echo -e "${YELLOW}⚠️  env.example not found. Creating basic .env file...${NC}"
        echo "GEMINI_API_KEY=your_api_key_here" > .env
        echo -e "${YELLOW}⚠️  Please edit backend/.env and add your GEMINI_API_KEY${NC}"
    fi
fi

cd ..

# Frontend setup
echo ""
echo -e "${BLUE}🎨 Setting up frontend...${NC}"
cd frontend

# Install dependencies
echo -e "${BLUE}Installing Node.js dependencies...${NC}"
npm install

# Verify Next.js installation
echo -e "${BLUE}Verifying Next.js installation...${NC}"
if npm list next >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Next.js installed successfully${NC}"
else
    echo -e "${RED}❌ Next.js installation failed${NC}"
    exit 1
fi

cd ..

echo ""
echo -e "${GREEN}🎉 Setup complete!${NC}"
echo ""
echo -e "${BLUE}📋 Next steps:${NC}"
echo -e "${YELLOW}1. Get a Google Gemini API key from: https://makersuite.google.com/app/apikey${NC}"
echo -e "${YELLOW}2. Edit backend/.env and add your GEMINI_API_KEY${NC}"
echo -e "${YELLOW}3. Run the start script to launch both services:${NC}"
echo -e "${BLUE}   ./start.sh${NC}"
echo ""
echo -e "${BLUE}   Or start services manually:${NC}"
echo -e "${BLUE}   Backend:  cd backend && source venv/bin/activate && python main.py${NC}"
echo -e "${BLUE}   Frontend: cd frontend && npm run dev${NC}"
echo ""
echo -e "${YELLOW}4. Install the Chrome extension:${NC}"
echo -e "${BLUE}   - Open chrome://extensions/${NC}"
echo -e "${BLUE}   - Enable Developer mode${NC}"
echo -e "${BLUE}   - Click 'Load unpacked' and select the chrome-extension/ folder${NC}"
echo ""
echo -e "${GREEN}🌐 Then visit http://localhost:3000 to start tracking your productivity!${NC}"
echo ""
echo -e "${BLUE}📚 For detailed instructions, see the README.md files in each directory.${NC}"
