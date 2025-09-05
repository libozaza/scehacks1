from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os
from dotenv import load_dotenv

from database import init_db
from models import Event, RepoPath
from file_tracker import FileTracker
from git_tracker import GitTracker
from gemini_service import GeminiService

# Load environment variables
load_dotenv()

# Global trackers
file_tracker = None
git_tracker = None
gemini_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    global gemini_service
    gemini_service = GeminiService()
    yield
    # Shutdown
    if file_tracker:
        file_tracker.stop()
    if git_tracker:
        git_tracker.stop()

app = FastAPI(
    title="What Did I Just Do?",
    description="Personal work activity tracker with AI insights",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "What Did I Just Do? API is running!"}

@app.post("/select-repo")
async def select_repo(repo_data: dict):
    """Select and start monitoring a repository"""
    global file_tracker, git_tracker
    
    folder_name = repo_data.get("folder_name")
    if not folder_name:
        raise HTTPException(status_code=400, detail="folder_name is required")
    
    # Resolve to absolute path
    repo_path = os.path.abspath(folder_name)
    
    # Validate that it exists and is a Git repo
    if not os.path.exists(repo_path):
        raise HTTPException(status_code=404, detail="Directory does not exist")
    
    git_dir = os.path.join(repo_path, ".git")
    if not os.path.exists(git_dir):
        raise HTTPException(status_code=400, detail="Directory is not a Git repository")
    
    # Stop existing trackers
    if file_tracker:
        file_tracker.stop()
    if git_tracker:
        git_tracker.stop()
    
    # Start new trackers
    file_tracker = FileTracker(repo_path)
    git_tracker = GitTracker(repo_path)
    
    file_tracker.start()
    git_tracker.start()
    
    # Store repo path in database
    await RepoPath.create_or_update(repo_path)
    
    return {"message": f"Started monitoring repository: {repo_path}"}

@app.get("/events")
async def get_events(hours: int = 3):
    """Get events from the last N hours"""
    events = await Event.get_recent_events(hours)
    return {"events": events}

@app.get("/daily-report")
async def get_daily_report():
    """Get AI-generated daily productivity report"""
    if not gemini_service:
        raise HTTPException(status_code=500, detail="Gemini service not initialized")
    
    events = await Event.get_daily_events()
    report = await gemini_service.generate_daily_report(events)
    return {"report": report}

@app.get("/suggestions")
async def get_suggestions():
    """Get smart suggestions based on activity"""
    if not gemini_service:
        raise HTTPException(status_code=500, detail="Gemini service not initialized")
    
    events = await Event.get_recent_events(24)  # Last 24 hours
    suggestions = await gemini_service.generate_suggestions(events)
    return {"suggestions": suggestions}

@app.post("/ask-gemini")
async def ask_gemini(question_data: dict):
    """Ask Gemini a question about recent activity"""
    if not gemini_service:
        raise HTTPException(status_code=500, detail="Gemini service not initialized")
    
    question = question_data.get("question")
    if not question:
        raise HTTPException(status_code=400, detail="question is required")
    
    events = await Event.get_recent_events(3)  # Last 3 hours
    answer = await gemini_service.answer_question(question, events)
    return {"answer": answer}

@app.post("/browser-event")
async def add_browser_event(event_data: dict):
    """Add browser activity event from Chrome extension"""
    event = await Event.create_browser_event(
        event_type=event_data.get("type"),
        url=event_data.get("url"),
        title=event_data.get("title"),
        details=event_data.get("details", {})
    )
    return {"message": "Browser event added", "event_id": event.id}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
