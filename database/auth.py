"""
Authentication models and utilities for PCOS Care
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime
from database.schema import Base


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

    # API Keys per servizi AI (Claude, OpenAI, etc.)
    anthropic_api_key = Column(String, nullable=True)
    openai_api_key = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"
