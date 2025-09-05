import asyncio
import git
from datetime import datetime
from typing import Dict, Any, Set
from models import Event
import os

class GitTracker:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.repo = git.Repo(repo_path)
        self.running = False
        self.last_commit_hash = None
        self.last_staged_files = set()
        self.last_pushed_commits = set()
        
        # Initialize with current state
        self._update_current_state()
    
    def _update_current_state(self):
        """Update current Git state"""
        try:
            # Get latest commit
            if self.repo.head.is_valid():
                self.last_commit_hash = self.repo.head.commit.hexsha
            
            # Get staged files
            self.last_staged_files = set(self.repo.index.diff("HEAD").iter_change_type('M'))
            self.last_staged_files.update(set(self.repo.index.diff("HEAD").iter_change_type('A')))
            
            # Get pushed commits (this is approximate - we track what we've seen)
            self.last_pushed_commits = set()
            
        except Exception as e:
            print(f"Error updating Git state: {e}")
    
    async def _check_git_changes(self):
        """Check for Git changes and create events"""
        try:
            # Check for new commits
            if self.repo.head.is_valid():
                current_commit = self.repo.head.commit.hexsha
                if self.last_commit_hash and current_commit != self.last_commit_hash:
                    # New commit detected
                    commit = self.repo.head.commit
                    await Event.create_git_event(
                        "git_commit",
                        git_hash=commit.hexsha,
                        git_message=commit.message.strip(),
                        details={
                            "author": commit.author.name,
                            "email": commit.author.email,
                            "date": commit.committed_datetime.isoformat(),
                            "files_changed": len(commit.stats.files)
                        }
                    )
                    self.last_commit_hash = current_commit
            
            # Check for staged files
            current_staged = set()
            for item in self.repo.index.diff("HEAD"):
                if item.change_type in ['M', 'A']:
                    current_staged.add(item.a_path)
            
            # Find newly staged files
            newly_staged = current_staged - self.last_staged_files
            for file_path in newly_staged:
                await Event.create_git_event(
                    "git_add",
                    details={
                        "file_path": file_path,
                        "action": "staged"
                    }
                )
            
            # Find unstaged files
            unstaged = self.last_staged_files - current_staged
            for file_path in unstaged:
                await Event.create_git_event(
                    "git_unstage",
                    details={
                        "file_path": file_path,
                        "action": "unstaged"
                    }
                )
            
            self.last_staged_files = current_staged
            
            # Check for pushes (this is tricky - we'll use a heuristic)
            # If there are commits that aren't in the remote, and then they disappear,
            # we assume they were pushed
            try:
                remote = self.repo.remotes.origin
                remote.fetch()
                
                # Get local commits not in remote
                local_commits = set()
                for commit in self.repo.iter_commits():
                    local_commits.add(commit.hexsha)
                
                remote_commits = set()
                for commit in self.repo.iter_commits(f"{remote.name}/main"):
                    remote_commits.add(commit.hexsha)
                
                # Commits that were local but are now in remote (likely pushed)
                newly_pushed = (self.last_pushed_commits | local_commits) & remote_commits - self.last_pushed_commits
                
                for commit_hash in newly_pushed:
                    commit = self.repo.commit(commit_hash)
                    await Event.create_git_event(
                        "git_push",
                        git_hash=commit_hash,
                        git_message=commit.message.strip(),
                        details={
                            "author": commit.author.name,
                            "files_changed": len(commit.stats.files)
                        }
                    )
                
                self.last_pushed_commits.update(newly_pushed)
                
            except Exception as e:
                # Remote operations might fail, that's okay
                pass
                
        except Exception as e:
            print(f"Error checking Git changes: {e}")
    
    async def _poll_loop(self):
        """Main polling loop"""
        while self.running:
            await self._check_git_changes()
            await asyncio.sleep(30)  # Poll every 30 seconds
    
    def start(self):
        """Start Git tracking"""
        if self.running:
            return
        
        self.running = True
        asyncio.create_task(self._poll_loop())
        print(f"Started Git tracking for: {self.repo_path}")
    
    def stop(self):
        """Stop Git tracking"""
        self.running = False
        print("Stopped Git tracking")
