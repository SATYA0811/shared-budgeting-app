"""
Authentication Routes - Step 1: Database & Authentication

This module handles:
- User registration with secure password hashing
- User login with JWT token generation
- User profile management
- Authentication middleware and security

Implements secure authentication using:
- JWT tokens for stateless authentication
- Bcrypt for password hashing
- Rate limiting to prevent abuse
- Input validation and error handling
"""

from fastapi import APIRouter, HTTPException, Depends, status, Request
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..database import get_db
from ..auth import authenticate_user, create_access_token, get_current_user, get_password_hash
from ..schemas import UserRegistration, UserLogin, Token, UserResponse
from ..models import User

# Create router
router = APIRouter(prefix="", tags=["Authentication"])

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

@router.post("/register", response_model=UserResponse)
@limiter.limit("5/minute")  # Limit registration attempts
def register(request: Request, user_data: UserRegistration, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hashed_password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "id": new_user.id,
        "name": new_user.name,
        "email": new_user.email,
        "created_at": new_user.created_at
    }

@router.post("/login", response_model=Token)
@limiter.limit("10/minute")  # Limit login attempts
def login(request: Request, login_data: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return access token."""
    user = authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "created_at": current_user.created_at
    }