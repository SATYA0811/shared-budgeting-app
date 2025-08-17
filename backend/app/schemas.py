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

# Category schemas
class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None
    default_budget: Optional[Decimal] = None

class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    parent_id: Optional[int]
    default_budget: Optional[Decimal]
    
    class Config:
        from_attributes = True

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None
    default_budget: Optional[Decimal] = None

# Transaction schemas
class TransactionCreate(BaseModel):
    account_id: Optional[int] = None
    date: datetime
    description: str
    amount: Decimal
    category_id: Optional[int] = None

class TransactionUpdate(BaseModel):
    account_id: Optional[int] = None
    date: Optional[datetime] = None
    description: Optional[str] = None
    amount: Optional[Decimal] = None
    category_id: Optional[int] = None

class TransactionResponse(BaseModel):
    id: int
    date: datetime
    description: str
    amount: Decimal
    category_id: Optional[int]
    account_id: Optional[int]
    user_id: Optional[int]
    source_file_id: Optional[int]
    category_name: Optional[str] = None
    
    class Config:
        from_attributes = True

# Categorization schemas
class CategoryRule(BaseModel):
    keywords: List[str]
    category_id: int
    priority: int = 1

class CategorizeTransactionRequest(BaseModel):
    transaction_ids: List[int]
    category_id: int

# Income schemas
class IncomeCreate(BaseModel):
    date: datetime
    amount: Decimal
    source: str
    notes: Optional[str] = None

class IncomeUpdate(BaseModel):
    date: Optional[datetime] = None
    amount: Optional[Decimal] = None
    source: Optional[str] = None
    notes: Optional[str] = None

class IncomeResponse(BaseModel):
    id: int
    date: datetime
    amount: Decimal
    source: str
    notes: Optional[str]
    user_id: int
    
    class Config:
        from_attributes = True

# Financial summary schemas
class FinancialSummary(BaseModel):
    total_income: Decimal
    total_expenses: Decimal
    net_balance: Decimal
    period_start: datetime
    period_end: datetime

class ExpenseSummary(BaseModel):
    category_name: str
    category_id: int
    total_amount: Decimal
    transaction_count: int
    budget_amount: Optional[Decimal]
    budget_remaining: Optional[Decimal]

class MonthlyTrend(BaseModel):
    month: str
    year: int
    income: Decimal
    expenses: Decimal
    net: Decimal

# Goal schemas
class GoalCreate(BaseModel):
    name: str
    target_amount: Decimal
    target_date: datetime
    recurrence: Optional[str] = None  # none, monthly, yearly
    current_amount: Optional[Decimal] = 0

class GoalUpdate(BaseModel):
    name: Optional[str] = None
    target_amount: Optional[Decimal] = None
    target_date: Optional[datetime] = None
    recurrence: Optional[str] = None
    current_amount: Optional[Decimal] = None

class GoalResponse(BaseModel):
    id: int
    name: str
    target_amount: Decimal
    current_amount: Decimal
    target_date: datetime
    recurrence: Optional[str]
    user_id: int
    progress_percentage: float
    amount_remaining: Decimal
    days_remaining: int
    is_achieved: bool
    
    class Config:
        from_attributes = True

class GoalContribution(BaseModel):
    goal_id: int
    amount: Decimal
    notes: Optional[str] = None

class GoalProgressUpdate(BaseModel):
    current_amount: Decimal

# Analytics schemas
class SpendingTrend(BaseModel):
    period: str  # "2024-01", "2024-02", etc.
    total_spending: Decimal
    transaction_count: int
    average_transaction: Decimal

class CategoryAnalysis(BaseModel):
    category_id: int
    category_name: str
    total_amount: Decimal
    transaction_count: int
    percentage_of_total: float
    average_per_transaction: Decimal
    budget_amount: Optional[Decimal] = None
    budget_utilization: Optional[float] = None

class MonthlyReport(BaseModel):
    month: str
    year: int
    total_income: Decimal
    total_expenses: Decimal
    net_savings: Decimal
    savings_rate: float
    top_categories: List[CategoryAnalysis]

class BudgetPerformance(BaseModel):
    category_id: int
    category_name: str
    budget_amount: Decimal
    actual_amount: Decimal
    variance: Decimal
    utilization_percentage: float
    status: str  # "under_budget", "over_budget", "on_track"

class FinancialInsight(BaseModel):
    type: str  # "warning", "suggestion", "achievement"
    title: str
    description: str
    category: Optional[str] = None
    amount: Optional[Decimal] = None