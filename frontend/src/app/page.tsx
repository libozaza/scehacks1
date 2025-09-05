"use client";

import { useState, useEffect } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { 
  Activity, 
  GitCommit, 
  FileText, 
  Globe, 
  FolderOpen, 
  Brain,
  Send,
  Clock,
  CheckCircle,
  AlertCircle
} from "lucide-react";
import { formatDistanceToNow } from "date-fns";

interface Event {
  id: number;
  event_type: string;
  timestamp: string;
  file_path?: string;
  git_hash?: string;
  git_message?: string;
  url?: string;
  title?: string;
  details?: any;
}

interface DailyReport {
  report: string;
}

interface Suggestions {
  suggestions: string[];
}

export default function Home() {
  const [events, setEvents] = useState<Event[]>([]);
  const [dailyReport, setDailyReport] = useState<DailyReport | null>(null);
  const [suggestions, setSuggestions] = useState<Suggestions | null>(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [selectedFolder, setSelectedFolder] = useState<string | null>(null);

  // Poll for events every 3 seconds
  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const response = await fetch("http://localhost:8000/events");
        const data = await response.json();
        setEvents(data.events || []);
      } catch (error) {
        console.error("Error fetching events:", error);
      }
    };

    fetchEvents();
    const interval = setInterval(fetchEvents, 3000);
    return () => clearInterval(interval);
  }, []);

  const fetchDailyReport = async () => {
    try {
      const response = await fetch("http://localhost:8000/daily-report");
      const data = await response.json();
      setDailyReport(data);
    } catch (error) {
      console.error("Error fetching daily report:", error);
    }
  };

  const fetchSuggestions = async () => {
    try {
      const response = await fetch("http://localhost:8000/suggestions");
      const data = await response.json();
      setSuggestions(data);
    } catch (error) {
      console.error("Error fetching suggestions:", error);
    }
  };

  const askQuestion = async () => {
    if (!question.trim()) return;
    
    setIsLoading(true);
    try {
      const response = await fetch("http://localhost:8000/ask-gemini", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question }),
      });
      const data = await response.json();
      setAnswer(data.answer);
    } catch (error) {
      console.error("Error asking question:", error);
      setAnswer("Error: Could not get answer from AI");
    } finally {
      setIsLoading(false);
    }
  };

  const handleFolderSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      const folderName = files[0].webkitRelativePath.split('/')[0];
      setSelectedFolder(folderName);
      
      try {
        const response = await fetch("http://localhost:8000/select-repo", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ folder_name: folderName }),
        });
        const data = await response.json();
        console.log("Repo selected:", data);
      } catch (error) {
        console.error("Error selecting repo:", error);
      }
    }
  };

  const getEventIcon = (eventType: string) => {
    if (eventType.startsWith('file_')) return <FileText className="h-4 w-4" />;
    if (eventType.startsWith('git_')) return <GitCommit className="h-4 w-4" />;
    if (eventType.startsWith('browser_')) return <Globe className="h-4 w-4" />;
    return <Activity className="h-4 w-4" />;
  };

  const getEventColor = (eventType: string) => {
    if (eventType.startsWith('file_')) return "bg-blue-100 text-blue-800";
    if (eventType.startsWith('git_')) return "bg-green-100 text-green-800";
    if (eventType.startsWith('browser_')) return "bg-purple-100 text-purple-800";
    return "bg-gray-100 text-gray-800";
  };

  const getEventDescription = (event: Event) => {
    if (event.event_type.startsWith('file_')) {
      return event.file_path || "Unknown file";
    }
    if (event.event_type.startsWith('git_')) {
      if (event.git_message) {
        return event.git_message.substring(0, 50) + (event.git_message.length > 50 ? "..." : "");
      }
      return event.event_type.replace('git_', '');
    }
    if (event.event_type.startsWith('browser_')) {
      return event.title || event.url || "Browser activity";
    }
    return event.event_type;
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            What Did I Just Do?
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Track your work activity with AI-powered insights
          </p>
        </div>

        <Tabs defaultValue="timeline" className="w-full">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="timeline">Timeline</TabsTrigger>
            <TabsTrigger value="report">Daily Report</TabsTrigger>
            <TabsTrigger value="suggestions">Suggestions</TabsTrigger>
            <TabsTrigger value="ask">Ask AI</TabsTrigger>
            <TabsTrigger value="repo">Select Repo</TabsTrigger>
          </TabsList>

          <TabsContent value="timeline" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  Activity Timeline
                </CardTitle>
                <CardDescription>
                  Real-time view of your file edits, Git activity, and browser interactions
                </CardDescription>
              </CardHeader>
              <CardContent>
                {events.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <Clock className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>No activity yet. Select a repository to start tracking!</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {events.map((event) => (
                      <div key={event.id} className="flex items-start gap-3 p-3 rounded-lg border bg-white dark:bg-gray-800">
                        <div className="flex-shrink-0 mt-1">
                          {getEventIcon(event.event_type)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <Badge className={getEventColor(event.event_type)}>
                              {event.event_type.replace('_', ' ')}
                            </Badge>
                            <span className="text-sm text-gray-500">
                              {formatDistanceToNow(new Date(event.timestamp), { addSuffix: true })}
                            </span>
                          </div>
                          <p className="text-sm text-gray-700 dark:text-gray-300">
                            {getEventDescription(event)}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="report" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Brain className="h-5 w-5" />
                  Daily Productivity Report
                </CardTitle>
                <CardDescription>
                  AI-generated summary of your coding activity
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button onClick={fetchDailyReport} className="mb-4">
                  Generate Report
                </Button>
                {dailyReport && (
                  <div className="prose dark:prose-invert max-w-none">
                    <p className="whitespace-pre-wrap">{dailyReport.report}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="suggestions" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5" />
                  Smart Suggestions
                </CardTitle>
                <CardDescription>
                  AI-powered productivity recommendations
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button onClick={fetchSuggestions} className="mb-4">
                  Get Suggestions
                </Button>
                {suggestions && (
                  <div className="space-y-2">
                    {suggestions.suggestions.map((suggestion, index) => (
                      <div key={index} className="flex items-start gap-2 p-3 rounded-lg bg-blue-50 dark:bg-blue-900/20">
                        <AlertCircle className="h-4 w-4 mt-1 text-blue-600 dark:text-blue-400" />
                        <p className="text-sm text-blue-800 dark:text-blue-200">{suggestion}</p>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="ask" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Brain className="h-5 w-5" />
                  Ask AI About Your Activity
                </CardTitle>
                <CardDescription>
                  Ask natural language questions about your recent work
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex gap-2">
                  <Input
                    placeholder="e.g., What files did I edit in the last 3 hours?"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && askQuestion()}
                  />
                  <Button onClick={askQuestion} disabled={isLoading || !question.trim()}>
                    <Send className="h-4 w-4" />
                  </Button>
                </div>
                {answer && (
                  <div className="p-4 rounded-lg bg-gray-50 dark:bg-gray-800">
                    <p className="whitespace-pre-wrap">{answer}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="repo" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FolderOpen className="h-5 w-5" />
                  Select Repository
                </CardTitle>
                <CardDescription>
                  Choose a Git repository to start tracking your activity
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <input
                      type="file"
                      webkitdirectory=""
                      directory=""
                      onChange={handleFolderSelect}
                      className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                    />
                  </div>
                  {selectedFolder && (
                    <div className="p-3 rounded-lg bg-green-50 dark:bg-green-900/20">
                      <p className="text-sm text-green-800 dark:text-green-200">
                        <CheckCircle className="h-4 w-4 inline mr-2" />
                        Monitoring repository: {selectedFolder}
                      </p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}