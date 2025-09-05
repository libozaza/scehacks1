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
    """Select and start monitoring a repository (legacy endpoint)"""
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

@app.post("/start-local-tracking")
async def start_local_tracking(tracking_data: dict):
    """Start tracking a local directory for file changes only"""
    global file_tracker
    
    local_directory_path = tracking_data.get("local_directory_path")
    if not local_directory_path:
        raise HTTPException(status_code=400, detail="local_directory_path is required")
    
    # Resolve to absolute path
    dir_path = os.path.abspath(local_directory_path)
    
    # Validate that it exists
    if not os.path.exists(dir_path):
        raise HTTPException(status_code=404, detail="Directory does not exist")
    
    if not os.path.isdir(dir_path):
        raise HTTPException(status_code=400, detail="Path is not a directory")
    
    # Stop existing file tracker
    if file_tracker:
        file_tracker.stop()
    
    # Start new file tracker
    file_tracker = FileTracker(dir_path)
    file_tracker.start()
    
    # Store directory path in database
    await RepoPath.create_or_update(dir_path)
    
    return {"message": f"Started tracking local directory: {dir_path}"}

@app.post("/start-git-tracking")
async def start_git_tracking(tracking_data: dict):
    """Start tracking a Git repository for commits and changes"""
    global git_tracker
    
    git_repo_path = tracking_data.get("git_repo_path")
    if not git_repo_path:
        raise HTTPException(status_code=400, detail="git_repo_path is required")
    
    # Resolve to absolute path
    repo_path = os.path.abspath(git_repo_path)
    
    # Validate that it exists and is a Git repo
    if not os.path.exists(repo_path):
        raise HTTPException(status_code=404, detail="Directory does not exist")
    
    git_dir = os.path.join(repo_path, ".git")
    if not os.path.exists(git_dir):
        raise HTTPException(status_code=400, detail="Directory is not a Git repository")
    
    # Stop existing git tracker
    if git_tracker:
        git_tracker.stop()
    
    # Start new git tracker
    git_tracker = GitTracker(repo_path)
    git_tracker.start()
    
    # Store repo path in database
    await RepoPath.create_or_update(repo_path)
    
    return {"message": f"Started tracking Git repository: {repo_path}"}

@app.post("/start-tracking")
async def start_tracking(tracking_data: dict):
    """Start tracking based on mode (local, git, or both)"""
    global file_tracker, git_tracker
    
    tracking_mode = tracking_data.get("tracking_mode", "local")
    local_directory_path = tracking_data.get("local_directory_path")
    git_repo_path = tracking_data.get("git_repo_path")
    
    if tracking_mode == "local":
        if not local_directory_path:
            raise HTTPException(status_code=400, detail="local_directory_path is required for local tracking")
        
        # Start local tracking
        dir_path = os.path.abspath(local_directory_path)
        if not os.path.exists(dir_path):
            raise HTTPException(status_code=404, detail="Local directory does not exist")
        
        if file_tracker:
            file_tracker.stop()
        file_tracker = FileTracker(dir_path)
        file_tracker.start()
        
        await RepoPath.create_or_update(dir_path)
        return {"message": f"Started local tracking: {dir_path}"}
    
    elif tracking_mode == "git":
        if not git_repo_path:
            raise HTTPException(status_code=400, detail="git_repo_path is required for git tracking")
        
        # Start git tracking
        repo_path = os.path.abspath(git_repo_path)
        if not os.path.exists(repo_path):
            raise HTTPException(status_code=404, detail="Git repository does not exist")
        
        git_dir = os.path.join(repo_path, ".git")
        if not os.path.exists(git_dir):
            raise HTTPException(status_code=400, detail="Directory is not a Git repository")
        
        if git_tracker:
            git_tracker.stop()
        git_tracker = GitTracker(repo_path)
        git_tracker.start()
        
        await RepoPath.create_or_update(repo_path)
        return {"message": f"Started git tracking: {repo_path}"}
    
    elif tracking_mode == "both":
        if not local_directory_path or not git_repo_path:
            raise HTTPException(status_code=400, detail="Both local_directory_path and git_repo_path are required for both tracking")
        
        # Start both trackers
        dir_path = os.path.abspath(local_directory_path)
        repo_path = os.path.abspath(git_repo_path)
        
        if not os.path.exists(dir_path):
            raise HTTPException(status_code=404, detail="Local directory does not exist")
        if not os.path.exists(repo_path):
            raise HTTPException(status_code=404, detail="Git repository does not exist")
        
        git_dir = os.path.join(repo_path, ".git")
        if not os.path.exists(git_dir):
            raise HTTPException(status_code=400, detail="Git repository path is not a valid Git repository")
        
        # Stop existing trackers
        if file_tracker:
            file_tracker.stop()
        if git_tracker:
            git_tracker.stop()
        
        # Start new trackers
        file_tracker = FileTracker(dir_path)
        git_tracker = GitTracker(repo_path)
        
        file_tracker.start()
        git_tracker.start()
        
        # Store both paths
        await RepoPath.create_or_update(dir_path)
        await RepoPath.create_or_update(repo_path)
        
        return {"message": f"Started tracking both local directory: {dir_path} and git repository: {repo_path}"}
    
    else:
        raise HTTPException(status_code=400, detail="Invalid tracking_mode. Must be 'local', 'git', or 'both'")

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

@app.delete("/clear-database")
async def clear_database():
    """Clear all events from the database"""
    try:
        await Event.clear_all_events()
        return {"message": "Database cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear database: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
