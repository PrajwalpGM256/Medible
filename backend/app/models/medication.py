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


class FoodLog(db.Model):
    """Track user's daily food intake"""
    
    __tablename__ = 'food_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Food info
    food_name = db.Column(db.String(255), nullable=False)
    fdc_id = db.Column(db.Integer, nullable=True)  # USDA FoodData Central ID
    brand_owner = db.Column(db.String(255), nullable=True)
    
    # Serving info
    servings = db.Column(db.Float, default=1.0, nullable=False)
    serving_size = db.Column(db.Float, nullable=True)
    serving_unit = db.Column(db.String(20), default='g', nullable=True)
    
    # Nutrition (per serving * servings)
    calories = db.Column(db.Float, nullable=True)
    protein = db.Column(db.Float, nullable=True)
    carbs = db.Column(db.Float, nullable=True)
    fat = db.Column(db.Float, nullable=True)
    fiber = db.Column(db.Float, nullable=True)
    sugar = db.Column(db.Float, nullable=True)
    sodium = db.Column(db.Float, nullable=True)
    
    # Meal info
    meal_type = db.Column(db.String(20), nullable=True)  # breakfast, lunch, dinner, snack
    notes = db.Column(db.Text, nullable=True)
    
    # When eaten
    logged_date = db.Column(db.Date, nullable=False, index=True)
    logged_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Interaction check
    had_interaction = db.Column(db.Boolean, nullable=True)
    interaction_count = db.Column(db.Integer, default=0, nullable=True)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "food_name": self.food_name,
            "fdc_id": self.fdc_id,
            "brand_owner": self.brand_owner,
            "servings": self.servings,
            "serving_size": self.serving_size,
            "serving_unit": self.serving_unit,
            "calories": self.calories,
            "protein": self.protein,
            "carbs": self.carbs,
            "fat": self.fat,
            "fiber": self.fiber,
            "sugar": self.sugar,
            "sodium": self.sodium,
            "meal_type": self.meal_type,
            "notes": self.notes,
            "logged_date": self.logged_date.isoformat() if self.logged_date else None,
            "logged_at": self.logged_at.isoformat() if self.logged_at else None,
            "had_interaction": self.had_interaction,
            "interaction_count": self.interaction_count,
        }
    
    @staticmethod
    def get_user_logs_by_date(user_id: int, date):
        """Get all food logs for a user on a specific date"""
        return FoodLog.query.filter_by(user_id=user_id, logged_date=date).order_by(FoodLog.logged_at).all()
    
    @staticmethod
    def get_user_logs_range(user_id: int, start_date, end_date):
        """Get food logs for a date range"""
        return FoodLog.query.filter(
            FoodLog.user_id == user_id,
            FoodLog.logged_date >= start_date,
            FoodLog.logged_date <= end_date
        ).order_by(FoodLog.logged_date.desc(), FoodLog.logged_at).all()
    
    @staticmethod
    def get_daily_totals(user_id: int, date) -> dict:
        """Get nutrition totals for a day"""
        logs = FoodLog.get_user_logs_by_date(user_id, date)
        totals = {
            "calories": 0, "protein": 0, "carbs": 0, "fat": 0,
            "fiber": 0, "sugar": 0, "sodium": 0, "food_count": len(logs)
        }
        for log in logs:
            if log.calories: totals["calories"] += log.calories
            if log.protein: totals["protein"] += log.protein
            if log.carbs: totals["carbs"] += log.carbs
            if log.fat: totals["fat"] += log.fat
            if log.fiber: totals["fiber"] += log.fiber
            if log.sugar: totals["sugar"] += log.sugar
            if log.sodium: totals["sodium"] += log.sodium
        return totals
    
    def __repr__(self):
        return f'<FoodLog {self.food_name} on {self.logged_date}>'


class InteractionCheck(db.Model):
    """Track user's interaction check history"""
    
    __tablename__ = 'interaction_checks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # What was checked
    food_name = db.Column(db.String(255), nullable=False)
    medications_checked = db.Column(db.Text, nullable=False)  # JSON string of medication names
    
    # Results
    had_interaction = db.Column(db.Boolean, default=False, nullable=False)
    interaction_count = db.Column(db.Integer, default=0, nullable=False)
    
    # Interaction details (JSON string with full interaction info)
    interactions_json = db.Column(db.Text, nullable=True)
    
    # Highest severity found
    max_severity = db.Column(db.String(20), nullable=True)  # high, moderate, low
    
    # Timestamp
    checked_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    
    def to_dict(self) -> dict:
        import json
        return {
            "id": self.id,
            "food_name": self.food_name,
            "medications_checked": json.loads(self.medications_checked) if self.medications_checked else [],
            "had_interaction": self.had_interaction,
            "interaction_count": self.interaction_count,
            "interactions": json.loads(self.interactions_json) if self.interactions_json else [],
            "max_severity": self.max_severity,
            "checked_at": self.checked_at.isoformat() if self.checked_at else None,
        }
    
    @staticmethod
    def get_user_history(user_id: int, limit: int = 50):
        """Get user's interaction check history"""
        return InteractionCheck.query.filter_by(user_id=user_id)\
            .order_by(InteractionCheck.checked_at.desc())\
            .limit(limit).all()
    
    @staticmethod
    def log_check(user_id: int, food_name: str, medications: list, interactions: list):
        """Log an interaction check"""
        import json
        
        # Determine max severity
        max_severity = None
        if interactions:
            severities = {'high': 3, 'moderate': 2, 'low': 1}
            max_sev_score = 0
            for interaction in interactions:
                sev = interaction.get('severity', 'low')
                if severities.get(sev, 0) > max_sev_score:
                    max_sev_score = severities[sev]
                    max_severity = sev
        
        check = InteractionCheck(
            user_id=user_id,
            food_name=food_name,
            medications_checked=json.dumps(medications),
            had_interaction=len(interactions) > 0,
            interaction_count=len(interactions),
            interactions_json=json.dumps(interactions) if interactions else None,
            max_severity=max_severity
        )
        db.session.add(check)
        db.session.commit()
        return check
    
    def __repr__(self):
        return f'<InteractionCheck {self.food_name} at {self.checked_at}>'