from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean
from sqlalchemy.sql import func
from database import Base
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, nullable=False)  # file_created, file_modified, git_add, git_commit, git_push, browser_tab, browser_click, etc.
    timestamp = Column(DateTime, default=func.now())
    file_path = Column(String, nullable=True)
    git_hash = Column(String, nullable=True)
    git_message = Column(Text, nullable=True)
    url = Column(String, nullable=True)
    title = Column(String, nullable=True)
    details = Column(JSON, nullable=True)  # Additional event-specific data
    
    @classmethod
    async def create_file_event(cls, event_type: str, file_path: str, details: Dict[str, Any] = None):
        """Create a file-related event"""
        from database import AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            event = cls(
                event_type=event_type,
                file_path=file_path,
                details=details or {}
            )
            session.add(event)
            await session.commit()
            await session.refresh(event)
            return event
    
    @classmethod
    async def create_git_event(cls, event_type: str, git_hash: str = None, git_message: str = None, details: Dict[str, Any] = None):
        """Create a Git-related event"""
        from database import AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            event = cls(
                event_type=event_type,
                git_hash=git_hash,
                git_message=git_message,
                details=details or {}
            )
            session.add(event)
            await session.commit()
            await session.refresh(event)
            return event
    
    @classmethod
    async def create_browser_event(cls, event_type: str, url: str = None, title: str = None, details: Dict[str, Any] = None):
        """Create a browser-related event"""
        from database import AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            event = cls(
                event_type=event_type,
                url=url,
                title=title,
                details=details or {}
            )
            session.add(event)
            await session.commit()
            await session.refresh(event)
            return event
    
    @classmethod
    async def get_recent_events(cls, hours: int = 3) -> List[Dict[str, Any]]:
        """Get events from the last N hours"""
        from database import AsyncSessionLocal
        from sqlalchemy import select
        
        async with AsyncSessionLocal() as session:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            result = await session.execute(
                select(cls).where(cls.timestamp >= cutoff_time).order_by(cls.timestamp.desc())
            )
            events = result.scalars().all()
            return [cls._event_to_dict(event) for event in events]
    
    @classmethod
    async def get_daily_events(cls) -> List[Dict[str, Any]]:
        """Get events from today"""
        from database import AsyncSessionLocal
        from sqlalchemy import select
        
        async with AsyncSessionLocal() as session:
            today = datetime.now().date()
            result = await session.execute(
                select(cls).where(
                    func.date(cls.timestamp) == today
                ).order_by(cls.timestamp.desc())
            )
            events = result.scalars().all()
            return [cls._event_to_dict(event) for event in events]
    
    @staticmethod
    def _event_to_dict(event) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            "id": event.id,
            "event_type": event.event_type,
            "timestamp": event.timestamp.isoformat(),
            "file_path": event.file_path,
            "git_hash": event.git_hash,
            "git_message": event.git_message,
            "url": event.url,
            "title": event.title,
            "details": event.details or {}
        }

class RepoPath(Base):
    __tablename__ = "repo_paths"
    
    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    @classmethod
    async def create_or_update(cls, path: str):
        """Create or update a repository path"""
        from database import AsyncSessionLocal
        from sqlalchemy import select
        
        async with AsyncSessionLocal() as session:
            # Check if path already exists
            result = await session.execute(select(cls).where(cls.path == path))
            existing = result.scalar_one_or_none()
            
            if existing:
                existing.is_active = True
                existing.updated_at = func.now()
                await session.commit()
                return existing
            else:
                # Deactivate all other paths
                await session.execute(
                    select(cls).update().values(is_active=False)
                )
                
                # Create new active path
                new_path = cls(path=path, is_active=True)
                session.add(new_path)
                await session.commit()
                await session.refresh(new_path)
                return new_path
