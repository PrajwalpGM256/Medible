"""
User Model
Handles user data and authentication
"""

from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(db.Model):
    """User account model"""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    last_login_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    medications = db.relationship('UserMedication', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    search_history = db.relationship('SearchHistory', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, email: str, password: str, first_name: str = None, last_name: str = None):
        self.email = email.lower().strip()
        self.set_password(password)
        self.first_name = first_name
        self.last_name = last_name
    
    def set_password(self, password: str):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
    
    def check_password(self, password: str) -> bool:
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login_at = datetime.now(timezone.utc)
        db.session.commit()
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or "User"
    
    def to_dict(self, include_email: bool = True) -> dict:
        """Serialize user to dictionary"""
        data = {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "medication_count": self.medications.count()
        }
        if include_email:
            data["email"] = self.email
        return data
    
    @staticmethod
    def find_by_email(email: str) -> 'User':
        """Find user by email"""
        return User.query.filter_by(email=email.lower().strip()).first()
    
    @staticmethod
    def find_by_id(user_id: int) -> 'User':
        """Find user by ID"""
        return User.query.get(user_id)
    
    def __repr__(self):
        return f'<User {self.email}>'