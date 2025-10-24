"""
Authentication utilities for WebApp API
- Password hashing
- JWT token generation/validation
- User authentication
"""

from datetime import datetime, timedelta
from typing import Optional
import bcrypt
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from database import DatabaseManager
from database.auth import User

# Security configuration
SECRET_KEY = "pcos-care-webapp-secret-key-change-in-production-2024"  # TODO: Move to env variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

# Database manager
db_manager = DatabaseManager()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def get_user_by_email(email: str) -> Optional[User]:
    """Get user by email"""
    session = db_manager.get_session()
    try:
        user = session.query(User).filter(User.email == email).first()
        return user
    finally:
        session.close()


def get_user_by_username(username: str) -> Optional[User]:
    """Get user by username"""
    session = db_manager.get_session()
    try:
        user = session.query(User).filter(User.username == username).first()
        return user
    finally:
        session.close()


def get_user_by_id(user_id: int) -> Optional[User]:
    """Get user by ID"""
    session = db_manager.get_session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        return user
    finally:
        session.close()


def authenticate_user(username_or_email: str, password: str) -> Optional[User]:
    """Authenticate a user by username/email and password"""
    # Try to find user by email first, then username
    user = get_user_by_email(username_or_email)
    if not user:
        user = get_user_by_username(username_or_email)

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


def create_user(email: str, username: str, password: str, full_name: Optional[str] = None) -> User:
    """Create a new user"""
    session = db_manager.get_session()

    try:
        # Check if user already exists
        existing_email = session.query(User).filter(User.email == email).first()
        if existing_email:
            raise ValueError("Email already registered")

        existing_username = session.query(User).filter(User.username == username).first()
        if existing_username:
            raise ValueError("Username already taken")

        # Create new user
        hashed_password = get_password_hash(password)
        new_user = User(
            email=email,
            username=username,
            hashed_password=hashed_password,
            full_name=full_name,
            is_active=True,
            created_at=datetime.utcnow()
        )

        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        return new_user

    finally:
        session.close()


def update_last_login(user_id: int):
    """Update user's last login timestamp"""
    session = db_manager.get_session()

    try:
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            user.last_login = datetime.utcnow()
            session.commit()
    finally:
        session.close()


async def get_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> Optional[User]:
    """
    Get current authenticated user from JWT token.
    Returns None if no token or invalid token (allowing public access).
    """
    if not token:
        return None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")

        if user_id is None:
            return None

        user = get_user_by_id(user_id)
        if user is None:
            return None

        if not user.is_active:
            return None

        return user

    except JWTError:
        return None


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get current active user - raises exception if not authenticated.
    Use this for protected endpoints.
    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    return current_user
