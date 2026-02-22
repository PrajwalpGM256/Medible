"""
Favorites & Reminders & Reports Models
Stores user favorites, medication reminders, and interaction reports
"""

import json
from datetime import datetime, timezone
from app import db


class FavoriteFood(db.Model):
    """User's favorite foods for quick access"""

    __tablename__ = 'favorite_foods'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    food_name = db.Column(db.String(255), nullable=False)
    fdc_id = db.Column(db.Integer, nullable=True)
    off_id = db.Column(db.String(100), nullable=True)
    source = db.Column(db.String(20), nullable=False, default='usda')  # usda, openfoodfacts
    nutrition_snapshot = db.Column(db.Text, nullable=True)  # JSON string
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'food_name', 'source', name='uq_user_food_source'),
    )

    def to_dict(self) -> dict:
        nutrition = None
        if self.nutrition_snapshot:
            try:
                nutrition = json.loads(self.nutrition_snapshot)
            except (json.JSONDecodeError, TypeError):
                nutrition = None

        return {
            "id": self.id,
            "food_name": self.food_name,
            "fdc_id": self.fdc_id,
            "off_id": self.off_id,
            "source": self.source,
            "nutrition": nutrition,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    @staticmethod
    def get_user_favorites(user_id: int):
        return FavoriteFood.query.filter_by(user_id=user_id).order_by(
            FavoriteFood.created_at.desc()
        ).all()

    def __repr__(self):
        return f'<FavoriteFood {self.food_name}>'


class MedicationReminder(db.Model):
    """Medication reminder schedule"""

    __tablename__ = 'medication_reminders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    medication_id = db.Column(db.Integer, db.ForeignKey('user_medications.id', ondelete='CASCADE'), nullable=False)
    reminder_time = db.Column(db.String(5), nullable=False)  # HH:MM format
    days_of_week = db.Column(db.Text, nullable=False, default='["mon","tue","wed","thu","fri","sat","sun"]')
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    medication = db.relationship('UserMedication', backref=db.backref('reminders', lazy='dynamic'))

    def to_dict(self) -> dict:
        days = []
        if self.days_of_week:
            try:
                days = json.loads(self.days_of_week)
            except (json.JSONDecodeError, TypeError):
                days = []

        return {
            "id": self.id,
            "medication_id": self.medication_id,
            "medication_name": self.medication.drug_name if self.medication else None,
            "reminder_time": self.reminder_time,
            "days_of_week": days,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    @staticmethod
    def get_user_reminders(user_id: int, active_only: bool = False):
        query = MedicationReminder.query.filter_by(user_id=user_id)
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(MedicationReminder.reminder_time).all()

    def __repr__(self):
        return f'<MedicationReminder {self.id} @ {self.reminder_time}>'


class InteractionReport(db.Model):
    """User-submitted missing interaction reports"""

    __tablename__ = 'interaction_reports'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    food_name = db.Column(db.String(255), nullable=False)
    drug_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    severity_suggestion = db.Column(db.String(20), nullable=True)  # low, medium, high
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, reviewed, accepted, rejected
    reviewer_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "food_name": self.food_name,
            "drug_name": self.drug_name,
            "description": self.description,
            "severity_suggestion": self.severity_suggestion,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<InteractionReport {self.food_name} + {self.drug_name}>'
