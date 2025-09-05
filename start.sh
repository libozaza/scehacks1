eract#!/bin/bash

# What Did I Just Do? - Start Script
echo "🚀 Starting What Did I Just Do? - Personal Work Activity Tracker"
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

# Function to check if a port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

# Function to kill processes on a specific port
kill_port() {
    local port=$1
    local pids=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pids" ]; then
        echo -e "${BLUE}   Killing processes on port $port: $pids${NC}"
        echo "$pids" | xargs kill -9 2>/dev/null
    fi
}

# Check prerequisites
echo -e "${BLUE}🔍 Checking prerequisites...${NC}"

if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 is required but not installed. Please install Python 3.8+ and try again.${NC}"
    exit 1
fi

if ! command_exists node; then
    echo -e "${RED}❌ Node.js is required but not installed. Please install Node.js 18+ and try again.${NC}"
    exit 1
fi

if ! command_exists npm; then
    echo -e "${RED}❌ npm is required but not installed. Please install npm and try again.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All prerequisites are installed${NC}"

# Check if setup has been run
if [ ! -d "backend/venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Running setup first...${NC}"
    if [ -f "setup.sh" ]; then
        chmod +x setup.sh
        ./setup.sh
    else
        echo -e "${RED}❌ setup.sh not found. Please run setup first.${NC}"
        exit 1
    fi
fi

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}⚠️  Backend .env file not found. Creating from template...${NC}"
    if [ -f "backend/env.example" ]; then
        cp backend/env.example backend/.env
        echo -e "${YELLOW}⚠️  Please edit backend/.env and add your GEMINI_API_KEY${NC}"
    else
        echo -e "${RED}❌ backend/env.example not found. Please create backend/.env manually.${NC}"
        exit 1
    fi
fi

# Check if node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${YELLOW}⚠️  Frontend dependencies not found. Installing...${NC}"
    cd frontend
    npm install
    cd ..
fi

# Check if ports are available
if port_in_use 8000; then
    echo -e "${RED}❌ Port 8000 is already in use. Please stop the service using that port and try again.${NC}"
    exit 1
fi

if port_in_use 3000; then
    echo -e "${RED}❌ Port 3000 is already in use. Please stop the service using that port and try again.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All checks passed${NC}"

# Function to cleanup background processes on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down services...${NC}"
    if [ ! -z "$BACKEND_PID" ]; then
        echo -e "${BLUE}   Stopping backend service (PID: $BACKEND_PID)...${NC}"
        kill -9 $BACKEND_PID 2>/dev/null
        echo -e "${BLUE}   Backend service stopped${NC}"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        echo -e "${BLUE}   Stopping frontend service (PID: $FRONTEND_PID)...${NC}"
        kill -9 $FRONTEND_PID 2>/dev/null
        echo -e "${BLUE}   Frontend service stopped${NC}"
    fi
    
    # Also kill any remaining processes on the ports (backup cleanup)
    echo -e "${BLUE}   Cleaning up any remaining processes on ports 8000 and 3000...${NC}"
    kill_port 8000
    kill_port 3000
    
    echo -e "${GREEN}✅ All services stopped${NC}"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start backend
echo -e "\n${BLUE}🔧 Starting backend service...${NC}"
cd backend

# Ensure virtual environment is activated and dependencies are installed
if [ ! -f "venv/bin/activate" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating...${NC}"
    python3 -m venv venv
fi

source venv/bin/activate

# Install/upgrade dependencies
echo -e "${BLUE}📦 Installing/updating Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Start the backend
echo -e "${BLUE}🚀 Starting FastAPI server...${NC}"
python main.py &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Check if backend started successfully
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}❌ Backend failed to start${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Backend service started (PID: $BACKEND_PID)${NC}"

# Start git tracking
echo -e "\n${BLUE}🔧 Setting up Git tracking...${NC}"
echo -e "${YELLOW}💡 Git tracking will monitor your repository for commits and pushes${NC}"

# Initialize git tracking status
GIT_REPO_STARTED=0

# Function to start git tracking
start_git_tracking() {
    local repo_path=$1
    echo -e "${BLUE}📁 Starting Git tracking for: $repo_path${NC}"
    
    # Make the API call to start git tracking
    local response=$(curl -s -X POST http://localhost:8000/start-git-tracking \
        -H "Content-Type: application/json" \
        -d "{\"git_repo_path\": \"$repo_path\"}")
    
    if echo "$response" | grep -q "Started tracking"; then
        echo -e "${GREEN}✅ Git tracking started successfully${NC}"
        GIT_REPO_STARTED=1
        return 0
    else
        echo -e "${RED}❌ Failed to start Git tracking: $response${NC}"
        return 1
    fi
}

# Try to detect current directory as git repo
if [ -d ".git" ]; then
    current_dir=$(pwd)
    echo -e "${BLUE}🔍 Detected Git repository in current directory: $current_dir${NC}"
    echo -e "${YELLOW}   Do you want to track this repository? (y/n)${NC}"
    read -p "   " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        start_git_tracking "$current_dir"
    fi
fi

# If no git repo detected or user declined, prompt for path
if [ -z "$GIT_REPO_STARTED" ]; then
    echo -e "${YELLOW}📁 Please enter the path to your Git repository to track:${NC}"
    echo -e "${BLUE}   (Leave empty to skip Git tracking)${NC}"
    read -p "   Git repo path: " git_repo_path
    
    if [ ! -z "$git_repo_path" ]; then
        # Expand tilde and resolve relative paths
        git_repo_path=$(eval echo "$git_repo_path")
        
        if [ -d "$git_repo_path" ] && [ -d "$git_repo_path/.git" ]; then
            start_git_tracking "$git_repo_path"
        else
            echo -e "${RED}❌ Invalid Git repository path: $git_repo_path${NC}"
            echo -e "${YELLOW}   Make sure the path exists and contains a .git directory${NC}"
        fi
    else
        echo -e "${BLUE}⏭️  Skipping Git tracking${NC}"
    fi
fi

# Start frontend
echo -e "\n${BLUE}🎨 Starting frontend service...${NC}"
cd frontend

# Ensure dependencies are installed
echo -e "${BLUE}📦 Installing/updating Node.js dependencies...${NC}"
npm install

# Start the frontend
echo -e "${BLUE}🚀 Starting Next.js development server...${NC}"
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait a moment for frontend to start
sleep 3

# Check if frontend started successfully
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "${RED}❌ Frontend failed to start${NC}"
    cleanup
    exit 1
fi

echo -e "${GREEN}✅ Frontend service started (PID: $FRONTEND_PID)${NC}"

# Display status
echo -e "\n${GREEN}🎉 All services are running!${NC}"
echo -e "${BLUE}================================================================${NC}"
echo -e "${BLUE}📊 Backend API:    http://localhost:8000${NC}"
echo -e "${BLUE}🌐 Frontend App:   http://localhost:3000${NC}"
echo -e "${BLUE}📚 API Docs:       http://localhost:8000/docs${NC}"
echo -e "${BLUE}================================================================${NC}"
echo -e "\n${YELLOW}💡 Tips:${NC}"
echo -e "   • Visit http://localhost:3000 to start tracking your productivity"
echo -e "   • Git tracking monitors commits and pushes automatically"
echo -e "   • Install the Chrome extension from the chrome-extension/ folder"
echo -e "   • Press Ctrl+C to stop all services"
echo -e "\n${BLUE}📋 Chrome Extension Setup:${NC}"
echo -e "   1. Open chrome://extensions/"
echo -e "   2. Enable Developer mode"
echo -e "   3. Click 'Load unpacked' and select the chrome-extension/ folder"
echo -e "\n${GREEN}🚀 Happy productivity tracking!${NC}"

# Wait for user to stop services
echo -e "\n${YELLOW}Press Ctrl+C to stop all services...${NC}"
wait
