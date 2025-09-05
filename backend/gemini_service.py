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
        self.model = genai.GenerativeModel('gemini-1.5-flash-lite')
    
    def _format_events_for_ai(self, events: List[Dict[str, Any]]) -> str:
        """Format events for AI consumption"""
        if not events:
            return "No events found."
        
        formatted = "Recent activity:\n\n"
        
        for event in events:
            timestamp = datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
            time_str = timestamp.strftime("%H:%M:%S")
            
            if event['event_type'].startswith('file_'):
                formatted += f"[{time_str}] {event['event_type']}: {event.get('file_path', 'Unknown file')}\n"
            elif event['event_type'].startswith('git_'):
                if event.get('git_message'):
                    formatted += f"[{time_str}] {event['event_type']}: {event['git_message'][:50]}...\n"
                else:
                    formatted += f"[{time_str}] {event['event_type']}\n"
            elif event['event_type'].startswith('browser_'):
                if event.get('title'):
                    formatted += f"[{time_str}] {event['event_type']}: {event['title']}\n"
                elif event.get('url'):
                    formatted += f"[{time_str}] {event['event_type']}: {event['url']}\n"
                else:
                    formatted += f"[{time_str}] {event['event_type']}\n"
        
        return formatted
    
    async def generate_daily_report(self, events: List[Dict[str, Any]]) -> str:
        """Generate AI-powered daily productivity report"""
        if not events:
            return "No activity recorded today. Start coding to see your productivity insights!"
        
        events_text = self._format_events_for_ai(events)
        
        prompt = f"""
        Analyze the following work activity data and create a concise, insightful daily productivity report.
        Focus on patterns, productivity insights, and actionable observations.
        
        {events_text}
        
        Please provide:
        1. A brief summary of the day's activity
        2. Key productivity patterns (coding vs browsing, commit frequency, etc.)
        3. Notable achievements or milestones
        4. One actionable suggestion for tomorrow
        
        Keep it concise but insightful, like a personal productivity coach.
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
