"""
User Medication Model
Stores user's saved medications for interaction checking
"""

from datetime import datetime, timezone
from app import db


class UserMedication(db.Model):
    """User's saved medication"""
    
    __tablename__ = 'user_medications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Drug identification
    drug_name = db.Column(db.String(255), nullable=False)
    brand_name = db.Column(db.String(255), nullable=True)
    generic_name = db.Column(db.String(255), nullable=True)
    
    # Dosage information
    dosage = db.Column(db.String(100), nullable=True)
    frequency = db.Column(db.String(100), nullable=True)
    
    # Additional info
    prescriber = db.Column(db.String(255), nullable=True)
    pharmacy = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('user_id', 'drug_name', name='unique_user_medication'),
    )
    
    def to_dict(self) -> dict:
        """Serialize medication to dictionary"""
        return {
            "id": self.id,
            "drug_name": self.drug_name,
            "brand_name": self.brand_name,
            "generic_name": self.generic_name,
            "dosage": self.dosage,
            "frequency": self.frequency,
            "prescriber": self.prescriber,
            "pharmacy": self.pharmacy,
            "notes": self.notes,
            "is_active": self.is_active,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @staticmethod
    def get_user_medications(user_id: int, active_only: bool = False):
        """Get all medications for a user"""
        query = UserMedication.query.filter_by(user_id=user_id)
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(UserMedication.drug_name).all()
    
    @staticmethod
    def get_user_medication_names(user_id: int, active_only: bool = True) -> list:
        """Get list of medication names for interaction checking"""
        meds = UserMedication.get_user_medications(user_id, active_only)
        return [med.drug_name for med in meds]
    
    def __repr__(self):
        return f'<UserMedication {self.drug_name} for User {self.user_id}>'


class SearchHistory(db.Model):
    """Track user search history for analytics"""
    
    __tablename__ = 'search_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True, index=True)
    
    search_type = db.Column(db.String(20), nullable=False)
    search_term = db.Column(db.String(255), nullable=False)
    results_count = db.Column(db.Integer, nullable=True)
    
    secondary_term = db.Column(db.String(255), nullable=True)
    had_interaction = db.Column(db.Boolean, nullable=True)
    
    searched_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "search_type": self.search_type,
            "search_term": self.search_term,
            "secondary_term": self.secondary_term,
            "results_count": self.results_count,
            "had_interaction": self.had_interaction,
            "searched_at": self.searched_at.isoformat() if self.searched_at else None
        }
    
    @staticmethod
    def log_search(search_type: str, search_term: str, user_id: int = None,
                   results_count: int = None, secondary_term: str = None,
                   had_interaction: bool = None):
        """Log a search to history"""
        history = SearchHistory(
            user_id=user_id,
            search_type=search_type,
            search_term=search_term,
            results_count=results_count,
            secondary_term=secondary_term,
            had_interaction=had_interaction
        )
        db.session.add(history)
        db.session.commit()
        return history