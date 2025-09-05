import os
import asyncio
import threading
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from models import Event
from typing import Dict, Any

class FileEventHandler(FileSystemEventHandler):
    def __init__(self):
        self.ignored_dirs = {'.git', '__pycache__', 'node_modules', '.next', 'dist', 'build'}
        self.ignored_extensions = {'.pyc', '.pyo', '.pyd', '.so', '.dylib', '.dll', '.db', '.sqlite', '.sqlite3'}
        self.ignored_patterns = {'whatido.db-journal', 'whatido.db-wal', 'whatido.db-shm'}
        self.loop = None
        self.last_event_time = {}
        self.throttle_seconds = 1  # Throttle events to max 1 per second per file
    
    def set_event_loop(self, loop):
        """Set the event loop for async operations"""
        self.loop = loop
    
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
        
        # Check for database file patterns
        filename = os.path.basename(path)
        if filename in self.ignored_patterns:
            return True
        
        # Check for any database-related files (journal, wal, shm files)
        if any(pattern in filename for pattern in ['.db-journal', '.db-wal', '.db-shm']):
            return True
        
        return False
    
    def on_created(self, event):
        if not event.is_directory and not self.should_ignore(event.src_path):
            self._schedule_event("file_created", event.src_path)
    
    def on_modified(self, event):
        if not event.is_directory and not self.should_ignore(event.src_path):
            self._schedule_event("file_modified", event.src_path)
    
    def on_deleted(self, event):
        if not event.is_directory and not self.should_ignore(event.src_path):
            self._schedule_event("file_deleted", event.src_path)
    
    def on_moved(self, event):
        if not event.is_directory:
            if not self.should_ignore(event.src_path) and not self.should_ignore(event.dest_path):
                self._schedule_event("file_renamed", event.dest_path, {
                    "old_path": event.src_path,
                    "new_path": event.dest_path
                })
    
    def _schedule_event(self, event_type: str, file_path: str, details: Dict[str, Any] = None):
        """Schedule async event creation with throttling"""
        current_time = time.time()
        last_time = self.last_event_time.get(file_path, 0)
        
        # Throttle events to prevent database overload
        if current_time - last_time < self.throttle_seconds:
            return
        
        self.last_event_time[file_path] = current_time
        
        if self.loop:
            asyncio.run_coroutine_threadsafe(
                self._create_event(event_type, file_path, details), 
                self.loop
            )
        else:
            print(f"Event loop not set, cannot create event: {event_type} for {file_path}")
    
    async def _create_event(self, event_type: str, file_path: str, details: Dict[str, Any] = None):
        """Create file event in database"""
        try:
            await Event.create_file_event(event_type, file_path, details)
            print(f"Created file event: {event_type} for {file_path}")
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
        
        # Set the event loop for async operations
        try:
            loop = asyncio.get_running_loop()
            self.event_handler.set_event_loop(loop)
        except RuntimeError:
            print("Warning: No event loop running, file events may not be created")
        
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
