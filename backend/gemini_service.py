import os
import google.generativeai as genai
from typing import List, Dict, Any
from datetime import datetime, timedelta

class GeminiService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def _format_events_for_ai(self, events: List[Dict[str, Any]]) -> str:
        """Format events for AI consumption with detailed information"""
        if not events:
            return "No events found."
        
        formatted = "Detailed Activity Timeline:\n\n"
        
        for event in events:
            timestamp = datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
            time_str = timestamp.strftime("%H:%M:%S")
            event_type = event.get('event_type', 'unknown')
            
            if event_type.startswith('git_'):
                git_hash = event.get('git_hash', '')
                git_message = event.get('git_message', '')
                details = event.get('details', {})
                author = details.get('author', 'Unknown')
                files_changed = details.get('files_changed', 0)
                
                formatted += f"🔧 [{time_str}] {event_type.replace('_', ' ').title()}\n"
                formatted += f"   Commit Hash: {git_hash}\n"
                formatted += f"   Message: {git_message}\n"
                formatted += f"   Author: {author}\n"
                formatted += f"   Total Files Changed: {files_changed}\n"
                
                if 'files' in details and details['files']:
                    formatted += "   File Changes:\n"
                    for file_info in details['files']:
                        path = file_info.get('path', 'Unknown')
                        insertions = file_info.get('insertions', 0)
                        deletions = file_info.get('deletions', 0)
                        lines = file_info.get('lines', 0)
                        formatted += f"     📄 {path}\n"
                        formatted += f"        +{insertions} additions, -{deletions} deletions ({lines} total lines)\n"
                formatted += "\n"
                
            elif event_type.startswith('file_'):
                file_path = event.get('file_path', 'Unknown file')
                formatted += f"📁 [{time_str}] {event_type.replace('_', ' ').title()}\n"
                formatted += f"   File Path: {file_path}\n"
                formatted += f"   Action: {event_type.replace('file_', '').replace('_', ' ').title()}\n\n"
                
            elif event_type.startswith('browser_'):
                url = event.get('url', 'Unknown URL')
                title = event.get('title', 'Unknown page')
                formatted += f"🌐 [{time_str}] {event_type.replace('_', ' ').title()}\n"
                formatted += f"   Page Title: {title}\n"
                formatted += f"   URL: {url}\n\n"
        
        return formatted
    
    async def generate_daily_report(self, events: List[Dict[str, Any]]) -> str:
        """Generate AI-powered daily productivity report"""
        if not events:
            return "No activity recorded today. Start coding to see your productivity insights!"
        
        events_text = self._format_events_for_ai(events)
        
        prompt = f"""
        Analyze the following work activity data and create a specific, concise daily productivity report.
        Focus on exact file changes, git interactions, and detailed coding activity.
        
        {events_text}
        
        Please provide a structured report with:
        1. **Activity Summary**: List specific files created/modified and git commits made
        2. **Git Activity**: Detail each commit with hash, message, and files changed
        3. **File Changes**: Specify which files were edited, created, or deleted
        4. **Productivity Insights**: Coding patterns, commit frequency, and work flow
        5. **Recommendations**: Specific actionable advice based on the actual work done
        
        Be precise about:
        - Exact file paths and names
        - Git commit hashes and messages
        - Number of lines added/removed per file
        - Time patterns of activity
        - Specific achievements and milestones
        
        Keep it detailed but concise, focusing on concrete actions and measurable progress.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating report: {str(e)}"
    
    async def generate_suggestions(self, events: List[Dict[str, Any]]) -> List[str]:
        """Generate smart suggestions based on activity"""
        if not events:
            return ["Start by selecting a repository to track your coding activity!"]
        
        events_text = self._format_events_for_ai(events)
        
        prompt = f"""
        Based on this work activity, provide 3-5 smart, actionable suggestions to improve productivity.
        Focus on patterns you notice and practical advice.
        
        {events_text}
        
        Provide suggestions as a simple list, each on a new line starting with "- ".
        Be specific and actionable.
        """
        
        try:
            response = self.model.generate_content(prompt)
            suggestions = [line.strip("- ").strip() for line in response.text.split("\n") if line.strip().startswith("-")]
            return suggestions[:5]  # Limit to 5 suggestions
        except Exception as e:
            return [f"Error generating suggestions: {str(e)}"]
    
    async def answer_question(self, question: str, events: List[Dict[str, Any]]) -> str:
        """Answer a natural language question about recent activity"""
        events_text = self._format_events_for_ai(events)
        
        prompt = f"""
        Based on the following work activity data, answer this question: "{question}"
        
        {events_text}
        
        Provide a clear, helpful answer. If the question can't be answered from the data, say so.
        Be conversational and helpful.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error answering question: {str(e)}"
