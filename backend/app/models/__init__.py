"""
Database Models
Import all models here for easy access and migration detection
"""

from app.models.user import User
from app.models.medication import UserMedication, SearchHistory

__all__ = ['User', 'UserMedication', 'SearchHistory']