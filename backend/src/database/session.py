"""
Database session management for TextRealmsAI.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os
import logging

logger = logging.getLogger(__name__)

# Database URL - can be overridden by environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./textrealms.db")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL logging
    pool_pre_ping=True,
    pool_recycle=300
)

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Get database session.
    
    Yields:
        Session: SQLAlchemy session
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def create_tables():
    """Create all database tables."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


def init_database():
    """Initialize the database."""
    try:
        create_tables()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


# Mock session for development/testing when database is not available
class MockSession:
    """Mock database session for development."""
    
    def query(self, *args, **kwargs):
        """Mock query method."""
        class MockQuery:
            def filter(self, *args, **kwargs):
                return self
            def filter_by(self, *args, **kwargs):
                return self
            def first(self):
                return None
            def all(self):
                return []
            def one_or_none(self):
                return None
        return MockQuery()
    
    def add(self, obj):
        """Mock add method."""
        pass
    
    def commit(self):
        """Mock commit method."""
        pass
    
    def rollback(self):
        """Mock rollback method."""
        pass
    
    def close(self):
        """Mock close method."""
        pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        pass


def get_mock_db() -> MockSession:
    """Get mock database session for development."""
    return MockSession()


# Auto-detect if we should use mock or real database
def get_session() -> Session:
    """
    Get database session with auto-fallback to mock.
    
    Returns:
        Session: Real or mock database session
    """
    try:
        return next(get_db())
    except Exception as e:
        logger.warning(f"Database not available, using mock session: {e}")
        return get_mock_db()
