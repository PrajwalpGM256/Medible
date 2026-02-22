"""
Token Blacklist Model
Stores invalidated JWT tokens for logout support
"""

from datetime import datetime, timezone
from app import db


class TokenBlacklist(db.Model):
    """Blacklisted JWT tokens"""

    __tablename__ = 'token_blacklist'

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(255), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    blacklisted_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)

    @staticmethod
    def is_blacklisted(jti: str) -> bool:
        """Check if a token JTI is blacklisted"""
        return TokenBlacklist.query.filter_by(jti=jti).first() is not None

    @staticmethod
    def blacklist_token(jti: str, user_id: int, expires_at: datetime):
        """Add a token to the blacklist"""
        entry = TokenBlacklist(jti=jti, user_id=user_id, expires_at=expires_at)
        db.session.add(entry)
        db.session.commit()
        return entry

    @staticmethod
    def cleanup_expired():
        """Remove expired tokens from blacklist"""
        TokenBlacklist.query.filter(
            TokenBlacklist.expires_at < datetime.now(timezone.utc)
        ).delete()
        db.session.commit()

    def __repr__(self):
        return f'<TokenBlacklist {self.jti}>'
