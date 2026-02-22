"""
Database Models
Import all models here for easy access and migration detection
"""

from app.models.user import User
from app.models.medication import UserMedication, SearchHistory, FoodLog, InteractionCheck
from app.models.token_blacklist import TokenBlacklist
from app.models.favorites import FavoriteFood, MedicationReminder, InteractionReport

__all__ = [
    'User', 'UserMedication', 'SearchHistory', 'FoodLog', 'InteractionCheck',
    'TokenBlacklist', 'FavoriteFood', 'MedicationReminder', 'InteractionReport'
]