"""
Database base module for TextRealmsAI.
"""

from sqlalchemy.ext.declarative import declarative_base

# Create declarative base for all database models
Base = declarative_base()

# Export for use in other modules
__all__ = ['Base']
