from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, func, JSON, Enum as SQLAlchemyEnum, Index
from sqlalchemy.orm import relationship
from enum import Enum

Base = declarative_base()

class Role(Enum):
    owner = "owner"
    admin = "admin"
    member = "member"

class AccountType(Enum):
    bank = "bank"
    card = "card"

class FileStatus(Enum):
    uploaded = "uploaded"
    parsing = "parsing"
    parsed = "parsed"
    error = "error"

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    household_memberships = relationship("HouseholdUser", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    incomes = relationship("Income", back_populates="user")
    goals = relationship("Goal", back_populates="user")
    files = relationship("File", back_populates="user")

class Household(Base):
    __tablename__ = 'households'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    members = relationship("HouseholdUser", back_populates="household")
    accounts = relationship("Account", back_populates="household")
    files = relationship("File", back_populates="household")

class HouseholdUser(Base):
    __tablename__ = 'household_users'
    id = Column(Integer, primary_key=True)
    household_id = Column(Integer, ForeignKey('households.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    role = Column(SQLAlchemyEnum(Role))
    
    # Relationships
    household = relationship("Household", back_populates="members")
    user = relationship("User", back_populates="household_memberships")

class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)
    household_id = Column(Integer, ForeignKey('households.id'))
    name = Column(String)
    type = Column(SQLAlchemyEnum(AccountType))
    last4 = Column(String)
    currency = Column(String)
    
    # Relationships
    household = relationship("Household", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account")

class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey('accounts.id'))
    bank_account_id = Column(Integer, ForeignKey('bank_accounts.id'))
    date = Column(DateTime)
    description = Column(String)
    amount = Column(Numeric)
    category_id = Column(Integer, ForeignKey('categories.id'))
    user_id = Column(Integer, ForeignKey('users.id')) # original uploader
    source_file_id = Column(Integer, ForeignKey('files.id'))
    is_recurring = Column(String, default='no')  # no, weekly, monthly, yearly
    notes = Column(String)
    tags = Column(JSON)  # Store tags as JSON array
    
    # Relationships
    account = relationship("Account", back_populates="transactions")
    bank_account = relationship("BankAccount", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
    user = relationship("User", back_populates="transactions")
    source_file = relationship("File", back_populates="transactions")
    
    # Indexes for better query performance
    __table_args__ = (
        Index('ix_transactions_user_id', 'user_id'),
        Index('ix_transactions_date', 'date'),
        Index('ix_transactions_category_id', 'category_id'),
        Index('ix_transactions_user_date', 'user_id', 'date'),
        Index('ix_transactions_user_category', 'user_id', 'category_id'),
        Index('ix_transactions_bank_account', 'bank_account_id'),
    )

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    parent_id = Column(Integer, ForeignKey('categories.id'))
    default_budget = Column(Numeric)
    
    # Relationships
    parent = relationship("Category", remote_side=[id])
    transactions = relationship("Transaction", back_populates="category")

class Income(Base):
    __tablename__ = 'incomes'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    date = Column(DateTime)
    amount = Column(Numeric)
    source = Column(String)
    notes = Column(String)
    
    # Relationships
    user = relationship("User", back_populates="incomes")
    
    # Indexes for better query performance
    __table_args__ = (
        Index('ix_incomes_user_id', 'user_id'),
        Index('ix_incomes_date', 'date'),
        Index('ix_incomes_user_date', 'user_id', 'date'),
    )

class GoalCategory(Enum):
    emergency = "emergency"
    home = "home"
    vacation = "vacation"
    car = "car"
    education = "education"
    retirement = "retirement"
    family = "family"
    health = "health"

class GoalStatus(Enum):
    active = "active"
    completed = "completed"
    paused = "paused"

class GoalPriority(Enum):
    low = "low"
    medium = "medium"
    high = "high"

class Goal(Base):
    __tablename__ = 'goals'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String)
    description = Column(String)
    target_amount = Column(Numeric)
    current_amount = Column(Numeric, default=0)
    monthly_contribution = Column(Numeric, default=0)
    target_date = Column(DateTime)
    category = Column(SQLAlchemyEnum(GoalCategory))
    status = Column(SQLAlchemyEnum(GoalStatus), default=GoalStatus.active)
    priority = Column(SQLAlchemyEnum(GoalPriority), default=GoalPriority.medium)
    recurrence = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="goals")
    contributions = relationship("GoalContribution", back_populates="goal")
    
    # Indexes for better query performance
    __table_args__ = (
        Index('ix_goals_user_id', 'user_id'),
        Index('ix_goals_target_date', 'target_date'),
        Index('ix_goals_status', 'status'),
        Index('ix_goals_category', 'category'),
    )

class GoalContribution(Base):
    __tablename__ = 'goal_contributions'
    id = Column(Integer, primary_key=True)
    goal_id = Column(Integer, ForeignKey('goals.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    amount = Column(Numeric)
    date = Column(DateTime, server_default=func.now())
    notes = Column(String)
    
    # Relationships
    goal = relationship("Goal", back_populates="contributions")
    user = relationship("User")

class BankAccount(Base):
    __tablename__ = 'bank_accounts'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    bank_name = Column(String)
    account_type = Column(String)  # Checking, Savings, Credit Card
    account_number_last4 = Column(String)
    balance = Column(Numeric, default=0)
    currency = Column(String, default='USD')
    is_active = Column(String, default='active')  # active, inactive, error
    last_sync = Column(DateTime)
    plaid_account_id = Column(String)  # For Plaid integration
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    transactions = relationship("Transaction", back_populates="bank_account")

class SharedExpense(Base):
    __tablename__ = 'shared_expenses'
    id = Column(Integer, primary_key=True)
    household_id = Column(Integer, ForeignKey('households.id'))
    transaction_id = Column(Integer, ForeignKey('transactions.id'))
    paid_by_user_id = Column(Integer, ForeignKey('users.id'))
    total_amount = Column(Numeric)
    split_method = Column(String, default='equal')  # equal, percentage, amount
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    household = relationship("Household")
    transaction = relationship("Transaction")
    paid_by = relationship("User")
    splits = relationship("SharedExpenseSplit", back_populates="shared_expense")

class SharedExpenseSplit(Base):
    __tablename__ = 'shared_expense_splits'
    id = Column(Integer, primary_key=True)
    shared_expense_id = Column(Integer, ForeignKey('shared_expenses.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    amount = Column(Numeric)
    percentage = Column(Numeric)  # If using percentage split
    is_paid = Column(String, default='pending')  # pending, paid
    
    # Relationships
    shared_expense = relationship("SharedExpense", back_populates="splits")
    user = relationship("User")

class FileType(Enum):
    bank_statement = "bank_statement"
    credit_statement = "credit_statement"
    csv = "csv"
    excel = "excel"

class File(Base):
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True)
    household_id = Column(Integer, ForeignKey('households.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    filename = Column(String)
    original_filename = Column(String)
    file_size = Column(Integer)
    file_type = Column(SQLAlchemyEnum(FileType))
    bank_name = Column(String)
    s3_key = Column(String)
    parsed_json_key = Column(String)
    status = Column(SQLAlchemyEnum(FileStatus))
    error_message = Column(String)
    transactions_found = Column(Integer, default=0)
    uploaded_at = Column(DateTime, server_default=func.now())
    processed_at = Column(DateTime)
    
    # Relationships
    household = relationship("Household", back_populates="files")
    user = relationship("User", back_populates="files")
    transactions = relationship("Transaction", back_populates="source_file")
