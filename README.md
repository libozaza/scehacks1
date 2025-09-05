# What Did I Just Do? 🚀

A full-stack personal work activity tracker that monitors file edits, Git activity, and browser interactions, then provides AI-powered insights and productivity reports.

## 🏆 Hackathon Project Features

- **Real-time Activity Tracking**: File edits, Git commits, browser interactions
- **AI-Powered Insights**: Daily reports and smart suggestions using Google Gemini
- **Natural Language Q&A**: Ask questions about your work activity
- **Live Timeline**: Real-time updates with beautiful UI
- **Privacy-First**: All data stored locally, no cloud tracking

## 🏗️ Architecture

```
whatido/
├── backend/          # FastAPI + SQLite + AI
├── frontend/         # Next.js + TailwindCSS + shadcn/ui
├── chrome-extension/ # Browser activity tracking
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- Google Gemini API key
- Git repository to track

### 1. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env and add your GEMINI_API_KEY

# Run the backend
python main.py
```

The backend will start on `http://localhost:8000`

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run the frontend
npm run dev
```

The frontend will start on `http://localhost:3000`

### 3. Chrome Extension Setup

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked" and select the `chrome-extension/` folder
4. The extension will appear in your toolbar

## 🎯 Demo Flow

1. **Select Repository**: Use the file picker to choose a Git repository
2. **Start Tracking**: The system begins monitoring file changes and Git activity
3. **Browse & Code**: Use your browser and edit files - everything is tracked
4. **View Timeline**: See real-time activity in the timeline view
5. **Get Insights**: Generate AI-powered daily reports and suggestions
6. **Ask Questions**: Use natural language to query your activity

## 🔧 API Endpoints

### Backend API (`http://localhost:8000`)

- `POST /select-repo` - Start monitoring a repository
- `GET /events` - Get recent activity events
- `GET /daily-report` - Generate AI daily report
- `GET /suggestions` - Get smart productivity suggestions
- `POST /ask-gemini` - Ask AI questions about activity
- `POST /browser-event` - Add browser activity (Chrome extension)

## 🎨 Frontend Features

### Timeline View
- Real-time activity feed
- Color-coded event types
- File edits, Git commits, browser interactions
- Live updates every 3 seconds

### Daily Report
- AI-generated productivity summary
- Coding vs browsing analysis
- Achievement highlights
- Actionable suggestions

### Smart Suggestions
- AI-powered productivity tips
- Pattern recognition
- Workflow optimization advice

### Ask AI Console
- Natural language queries
- "What files did I edit today?"
- "Did I push my code?"
- "How much time did I spend coding?"

### Repository Selection
- File picker for easy repo selection
- Automatic Git validation
- Real-time monitoring status

## 🔍 Chrome Extension Features

### Privacy-First Tracking
- No sensitive data collection
- Skips password fields
- Throttled event tracking
- Local data storage only

### Activity Types Tracked
- Tab creation/navigation/closure
- Link and button clicks
- Form interactions (non-sensitive)
- Keyboard shortcuts
- Scroll behavior
- Focus/blur events

### Extension UI
- Toggle tracking on/off
- Real-time status indicator
- Direct link to dashboard
- Privacy information

## 🛠️ Technical Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLite**: Local database storage
- **Watchdog**: File system monitoring
- **GitPython**: Git repository tracking
- **Google Gemini**: AI-powered insights
- **AsyncIO**: Concurrent event handling

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **TailwindCSS**: Utility-first styling
- **shadcn/ui**: Beautiful component library
- **Lucide React**: Icon library
- **date-fns**: Date manipulation

### Chrome Extension
- **Manifest V3**: Latest extension standard
- **Service Worker**: Background processing
- **Content Scripts**: Page interaction tracking
- **Chrome APIs**: Tab and window management

## 🔐 Privacy & Security

- **Local Storage**: All data stays on your machine
- **No Cloud Sync**: No external data transmission
- **Sensitive Data Protection**: Passwords and personal info never tracked
- **User Control**: Full control over what gets tracked
- **Open Source**: Transparent codebase

## 🎯 Hackathon Highlights

### Best Overall Track
- ✅ Polished timeline with live updates
- ✅ AI summaries and natural language Q&A
- ✅ Smart suggestions and productivity insights
- ✅ Beautiful, responsive UI
- ✅ Real-time data synchronization

### Most Likely to Be a Startup
- ✅ Automatic productivity tracking
- ✅ AI-powered insights and recommendations
- ✅ Privacy-first approach
- ✅ Potential SaaS model ("Fitbit for your workday")
- ✅ Scalable architecture

## 🚀 Future Enhancements

- **Team Collaboration**: Multi-user tracking and insights
- **Productivity Metrics**: Time tracking and efficiency scores
- **Integration Hub**: Connect with GitHub, Slack, etc.
- **Mobile App**: iOS/Android companion apps
- **Advanced Analytics**: Machine learning insights
- **Export Features**: Data export and reporting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Google Gemini for AI capabilities
- shadcn/ui for beautiful components
- FastAPI and Next.js communities
- All open source contributors

---

**Built with ❤️ for the hackathon** - Track your productivity, understand your patterns, and optimize your workflow!
