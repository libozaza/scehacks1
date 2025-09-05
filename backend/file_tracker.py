import os
import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from models import Event
from typing import Dict, Any

class FileEventHandler(FileSystemEventHandler):
    def __init__(self):
        self.ignored_dirs = {'.git', '__pycache__', 'node_modules', '.next', 'dist', 'build'}
        self.ignored_extensions = {'.pyc', '.pyo', '.pyd', '.so', '.dylib', '.dll'}
    
    def should_ignore(self, path: str) -> bool:
        """Check if file should be ignored"""
        # Check if any part of the path contains ignored directories
        path_parts = path.split(os.sep)
        if any(part in self.ignored_dirs for part in path_parts):
            return True
        
        # Check file extension
        _, ext = os.path.splitext(path)
        if ext in self.ignored_extensions:
            return True
        
        return False
    
    def on_created(self, event):
        if not event.is_directory and not self.should_ignore(event.src_path):
            asyncio.create_task(self._create_event("file_created", event.src_path))
    
    def on_modified(self, event):
        if not event.is_directory and not self.should_ignore(event.src_path):
            asyncio.create_task(self._create_event("file_modified", event.src_path))
    
    def on_deleted(self, event):
        if not event.is_directory and not self.should_ignore(event.src_path):
            asyncio.create_task(self._create_event("file_deleted", event.src_path))
    
    def on_moved(self, event):
        if not event.is_directory:
            if not self.should_ignore(event.src_path) and not self.should_ignore(event.dest_path):
                asyncio.create_task(self._create_event("file_renamed", event.dest_path, {
                    "old_path": event.src_path,
                    "new_path": event.dest_path
                }))
    
    async def _create_event(self, event_type: str, file_path: str, details: Dict[str, Any] = None):
        """Create file event in database"""
        try:
            await Event.create_file_event(event_type, file_path, details)
        except Exception as e:
            print(f"Error creating file event: {e}")

class FileTracker:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.observer = None
        self.event_handler = FileEventHandler()
    
    def start(self):
        """Start file tracking"""
        if self.observer and self.observer.is_alive():
            self.stop()
        
        self.observer = Observer()
        self.observer.schedule(self.event_handler, self.repo_path, recursive=True)
        self.observer.start()
        print(f"Started file tracking for: {self.repo_path}")
    
    def stop(self):
        """Stop file tracking"""
        if self.observer and self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
            print("Stopped file tracking")
