# Backend - What Did I Just Do?

FastAPI backend for personal work activity tracking with AI-powered insights.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp env.example .env
# Edit .env and add your GEMINI_API_KEY

# Run the server
python main.py
```

## 🔧 Environment Variables

Create a `.env` file with:

```env
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=sqlite:///./whatido.db
```

## 📡 API Endpoints

### Repository Management
- `POST /select-repo` - Start monitoring a Git repository

### Activity Tracking
- `GET /events?hours=3` - Get recent events (default: last 3 hours)
- `POST /browser-event` - Add browser activity from Chrome extension

### AI Insights
- `GET /daily-report` - Generate AI-powered daily productivity report
- `GET /suggestions` - Get smart productivity suggestions
- `POST /ask-gemini` - Ask natural language questions about activity

## 🗄️ Database Schema

### Events Table
- `id`: Primary key
- `event_type`: Type of event (file_created, git_commit, browser_click, etc.)
- `timestamp`: When the event occurred
- `file_path`: File path (for file events)
- `git_hash`: Git commit hash (for Git events)
- `git_message`: Git commit message
- `url`: URL (for browser events)
- `title`: Page title (for browser events)
- `details`: JSON with additional event data

### RepoPaths Table
- `id`: Primary key
- `path`: Repository path
- `is_active`: Whether this repo is currently being monitored
- `created_at`: When monitoring started
- `updated_at`: Last update time

## 🔍 Event Types

### File Events
- `file_created`: New file created
- `file_modified`: File content changed
- `file_deleted`: File removed
- `file_renamed`: File moved/renamed

### Git Events
- `git_add`: File staged for commit
- `git_unstage`: File unstaged
- `git_commit`: New commit created
- `git_push`: Commits pushed to remote

### Browser Events
- `browser_tab_created`: New tab opened
- `browser_navigation`: Page navigation
- `browser_tab_closed`: Tab closed
- `browser_click`: Link/button clicked
- `browser_typing`: Text input
- `browser_shortcut`: Keyboard shortcut used
- `browser_focus`: Form field focused
- `browser_blur`: Form field unfocused
- `browser_scroll`: Page scrolled

## 🤖 AI Integration

The backend uses Google Gemini API for:

- **Daily Reports**: Summarize daily activity with insights
- **Smart Suggestions**: Provide productivity recommendations
- **Q&A**: Answer natural language questions about activity

## 🔧 Development

### Running in Development
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Database Migrations
The database is automatically initialized when the app starts. Tables are created if they don't exist.

### File Tracking
Uses the `watchdog` library to monitor file system changes in real-time.

### Git Tracking
Uses `GitPython` to monitor Git repository changes with 30-second polling.

## 🐛 Troubleshooting

### Common Issues

1. **Gemini API Error**: Make sure your API key is set in `.env`
2. **File Tracking Not Working**: Ensure the repository path is valid and accessible
3. **Git Tracking Issues**: Verify the directory is a Git repository
4. **Database Errors**: Check file permissions for SQLite database

### Logs
The application logs to console. Check for error messages and stack traces.

## 📦 Dependencies

- `fastapi`: Web framework
- `uvicorn`: ASGI server
- `sqlalchemy`: Database ORM
- `aiosqlite`: Async SQLite driver
- `watchdog`: File system monitoring
- `GitPython`: Git repository access
- `google-generativeai`: Gemini AI integration
- `python-dotenv`: Environment variable management
