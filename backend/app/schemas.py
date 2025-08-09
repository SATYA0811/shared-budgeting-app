from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

# Auth schemas
class UserRegistration(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Household schemas
class HouseholdCreate(BaseModel):
    name: str

class HouseholdResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class HouseholdInvite(BaseModel):
    email: EmailStr
    role: str  # owner, admin, member

# Account schemas
class AccountCreate(BaseModel):
    name: str
    type: str  # bank, card
    last4: str
    currency: str = "USD"

class AccountResponse(BaseModel):
    id: int
    name: str
    type: str
    last4: str
    currency: str
    
    class Config:
        from_attributes = True

# Transaction schemas
class TransactionResponse(BaseModel):
    id: int
    date: datetime
    description: str
    amount: Decimal
    category_id: Optional[int]
    
    class Config:
        from_attributes = True