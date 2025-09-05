# Chrome Extension - What Did I Just Do?

Browser activity tracking extension for the personal work activity tracker.

## 🚀 Installation

### Development Installation
1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select the `chrome-extension/` folder
5. The extension will appear in your toolbar

### Production Installation
1. Package the extension as a `.zip` file
2. Upload to Chrome Web Store (when ready for distribution)

## 🔍 Features

### Privacy-First Tracking
- **No Sensitive Data**: Passwords, emails, and personal info are never tracked
- **Throttled Events**: Prevents spam by limiting event frequency
- **User Control**: Toggle tracking on/off anytime
- **Local Storage**: All data stays on your machine

### Activity Types Tracked

#### Tab Management
- `browser_tab_created`: New tab opened
- `browser_navigation`: Page navigation/refresh
- `browser_tab_closed`: Tab closed
- `browser_window_focus`: Window focused
- `browser_window_blur`: Window unfocused

#### User Interactions
- `browser_click`: Links and buttons clicked
- `browser_typing`: Text input (non-sensitive fields only)
- `browser_shortcut`: Keyboard shortcuts (Ctrl+C, Cmd+S, etc.)
- `browser_focus`: Form fields focused
- `browser_blur`: Form fields unfocused
- `browser_scroll`: Page scrolling (throttled)

### Extension UI
- **Status Indicator**: Shows tracking status (active/inactive)
- **Toggle Button**: Start/stop tracking
- **Dashboard Link**: Direct access to main app
- **Privacy Info**: Clear explanation of what's tracked

## 🛠️ Technical Details

### Manifest V3
- Latest Chrome extension standard
- Service worker for background processing
- Content scripts for page interaction
- Minimal permissions for privacy

### Permissions
```json
{
  "permissions": ["tabs", "activeTab", "storage"],
  "host_permissions": ["http://localhost:8000/*"]
}
```

### File Structure
```
chrome-extension/
├── manifest.json      # Extension configuration
├── background.js      # Service worker
├── content.js         # Content script
├── popup.html         # Extension popup UI
├── popup.js           # Popup functionality
└── icon*.png          # Extension icons
```

## 🔧 Development

### Background Script (`background.js`)
- Handles tab events (create, update, remove)
- Manages window focus/blur
- Processes messages from content script
- Sends data to backend API

### Content Script (`content.js`)
- Injected into all web pages
- Tracks user interactions
- Throttles events to prevent spam
- Sends activity data to background script

### Popup (`popup.html` + `popup.js`)
- Extension UI when clicked
- Shows tracking status
- Toggle tracking on/off
- Links to main dashboard

## 🔐 Privacy & Security

### What's NOT Tracked
- Password fields
- Email addresses
- Phone numbers
- Credit card information
- Personal identification data

### What IS Tracked
- Page URLs (for context)
- Page titles
- Click targets (links, buttons)
- Form field types (not content)
- Keyboard shortcuts
- Scroll behavior

### Data Flow
1. User interacts with webpage
2. Content script captures event
3. Event is filtered for privacy
4. Data sent to background script
5. Background script sends to backend
6. Backend stores in local database

## 🎯 Usage

### First Time Setup
1. Install the extension
2. Click the extension icon
3. Click "Start Tracking"
4. Open the main dashboard at `http://localhost:3000`

### Daily Usage
1. Extension runs automatically in background
2. Click icon to check status
3. Toggle tracking as needed
4. View activity in main dashboard

### Troubleshooting
- **Not Tracking**: Check if backend is running on port 8000
- **Permission Errors**: Ensure extension has required permissions
- **Data Not Appearing**: Verify backend API is accessible

## 🔧 Customization

### Adding New Event Types
1. Update `content.js` to capture new events
2. Add event handling in `background.js`
3. Update backend to process new event type
4. Modify frontend to display new events

### Changing API Endpoint
1. Update `API_BASE` in `background.js`
2. Update `host_permissions` in `manifest.json`
3. Ensure CORS is configured on backend

### Styling Changes
1. Modify `popup.html` for UI changes
2. Update CSS in popup for styling
3. Test across different screen sizes

## 🚀 Production Deployment

### Preparing for Chrome Web Store
1. Create proper icons (16x16, 48x48, 128x128)
2. Add detailed description and screenshots
3. Test thoroughly on different websites
4. Ensure privacy policy is clear
5. Package as `.zip` file

### Distribution
- Chrome Web Store (recommended)
- Developer mode installation
- Enterprise distribution

## 🐛 Common Issues

### Extension Not Loading
- Check manifest.json syntax
- Verify all files are present
- Check Chrome console for errors

### Tracking Not Working
- Ensure backend is running
- Check network connectivity
- Verify API endpoint is correct

### Permission Errors
- Review manifest permissions
- Check host permissions
- Ensure user granted permissions

## 📊 Analytics

The extension tracks its own performance:
- Event capture rate
- API response times
- Error rates
- User engagement

This data helps improve the extension and identify issues.

## 🔄 Updates

### Automatic Updates
- Chrome handles extension updates
- Users receive updates automatically
- No manual intervention required

### Version Management
- Update version in `manifest.json`
- Test thoroughly before release
- Document changes in release notes
