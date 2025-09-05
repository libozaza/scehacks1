# Frontend - What Did I Just Do?

Next.js frontend with TailwindCSS and shadcn/ui for the personal work activity tracker.

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

The app will be available at `http://localhost:3000`

## 🎨 Features

### Timeline View
- Real-time activity feed with live updates
- Color-coded event types (file, Git, browser)
- Hover tooltips with event details
- Auto-refresh every 3 seconds

### Daily Report
- AI-generated productivity summary
- One-click report generation
- Insights into coding vs browsing patterns

### Smart Suggestions
- AI-powered productivity recommendations
- Pattern-based suggestions
- Actionable advice for workflow improvement

### Ask AI Console
- Natural language queries about activity
- Examples:
  - "What files did I edit today?"
  - "Did I push my code?"
  - "How much time did I spend coding?"

### Repository Selection
- File picker for easy repo selection
- Automatic validation and monitoring setup
- Real-time status updates

## 🛠️ Tech Stack

- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **TailwindCSS**: Utility-first CSS framework
- **shadcn/ui**: Beautiful, accessible components
- **Lucide React**: Icon library
- **date-fns**: Date manipulation utilities

## 🎨 UI Components

### shadcn/ui Components Used
- `Button`: Interactive buttons with variants
- `Card`: Content containers with headers
- `Badge`: Status indicators and labels
- `Input`: Form input fields
- `Textarea`: Multi-line text input
- `Tabs`: Tabbed navigation
- `Separator`: Visual dividers

### Custom Components
- Event timeline with icons and timestamps
- Real-time status indicators
- AI response display areas
- File picker integration

## 🔄 Data Flow

1. **Polling**: Frontend polls `/events` every 3 seconds
2. **Real-time Updates**: Timeline updates automatically
3. **User Actions**: Generate reports, ask questions, select repos
4. **API Integration**: All backend communication via REST API

## 🎯 Key Features

### Live Timeline
```typescript
// Auto-refresh events every 3 seconds
useEffect(() => {
  const fetchEvents = async () => {
    const response = await fetch("http://localhost:8000/events");
    const data = await response.json();
    setEvents(data.events || []);
  };

  fetchEvents();
  const interval = setInterval(fetchEvents, 3000);
  return () => clearInterval(interval);
}, []);
```

### Event Type Icons
- File events: `FileText` icon
- Git events: `GitCommit` icon  
- Browser events: `Globe` icon
- Default: `Activity` icon

### Color Coding
- File events: Blue badges
- Git events: Green badges
- Browser events: Purple badges
- Default: Gray badges

## 🎨 Styling

### Dark Mode Support
- Automatic dark mode detection
- TailwindCSS dark mode classes
- Consistent color scheme

### Responsive Design
- Mobile-first approach
- Flexible grid layouts
- Touch-friendly interactions

### Animations
- Smooth transitions
- Hover effects
- Loading states

## 🔧 Development

### Available Scripts
```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
```

### Environment Variables
No environment variables required for frontend - connects to backend at `http://localhost:8000`

### Code Structure
```
src/
├── app/
│   ├── globals.css      # Global styles
│   ├── layout.tsx       # Root layout
│   └── page.tsx         # Main page component
├── components/
│   └── ui/              # shadcn/ui components
└── lib/
    └── utils.ts         # Utility functions
```

## 🎯 User Experience

### Intuitive Navigation
- Tab-based interface
- Clear visual hierarchy
- Consistent interaction patterns

### Real-time Feedback
- Live activity updates
- Status indicators
- Loading states

### Accessibility
- Keyboard navigation
- Screen reader support
- High contrast colors
- Focus indicators

## 🚀 Production Build

```bash
# Build for production
npm run build

# Start production server
npm run start
```

The built app will be optimized and ready for deployment.

## 🔧 Customization

### Adding New Event Types
1. Update the `getEventIcon()` function
2. Add color scheme in `getEventColor()`
3. Update description logic in `getEventDescription()`

### Styling Changes
- Modify `globals.css` for global styles
- Use TailwindCSS classes for component styling
- Customize shadcn/ui theme in `components.json`

### API Integration
- Update API endpoints in fetch calls
- Add error handling for network requests
- Implement retry logic for failed requests