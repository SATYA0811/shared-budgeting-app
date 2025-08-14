
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, func, JSON, Enum as SQLAlchemyEnum
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

class FileType(Enum):
    bank_statement = "bank_statement"
    receipt = "receipt"
    invoice = "invoice"
    other = "other"

class GoalStatus(Enum):
    active = "active"
    completed = "completed"
    paused = "paused"

class GoalPriority(Enum):
    low = "low"
    medium = "medium"
    high = "high"

class GoalCategory(Enum):
    emergency = "emergency"
    vacation = "vacation"
    debt = "debt"
    retirement = "retirement"
    other = "other"

class ExpenseStatus(Enum):
    pending = "pending"
    settled = "settled"

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
    date = Column(DateTime)
    description = Column(String)
    amount = Column(Numeric)
    category_id = Column(Integer, ForeignKey('categories.id'))
    user_id = Column(Integer, ForeignKey('users.id')) # original uploader
    source_file_id = Column(Integer, ForeignKey('files.id'))
    
    # Relationships
    account = relationship("Account", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
    user = relationship("User", back_populates="transactions")
    source_file = relationship("File", back_populates="transactions")

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

class Goal(Base):
    __tablename__ = 'goals'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String)
    target_amount = Column(Numeric)
    current_amount = Column(Numeric)
    target_date = Column(DateTime)
    recurrence = Column(String)
    status = Column(SQLAlchemyEnum(GoalStatus))
    priority = Column(SQLAlchemyEnum(GoalPriority))
    category = Column(SQLAlchemyEnum(GoalCategory))
    
    # Relationships
    user = relationship("User", back_populates="goals")
    contributions = relationship("GoalContribution", back_populates="goal")

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

class File(Base):
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True)
    household_id = Column(Integer, ForeignKey('households.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    s3_key = Column(String)
    parsed_json_key = Column(String)
    status = Column(SQLAlchemyEnum(FileStatus))
    
    # Relationships
    household = relationship("Household", back_populates="files")
    user = relationship("User", back_populates="files")
    transactions = relationship("Transaction", back_populates="source_file")

class SharedExpense(Base):
    __tablename__ = 'shared_expenses'
    id = Column(Integer, primary_key=True)
    household_id = Column(Integer, ForeignKey('households.id'))
    payer_id = Column(Integer, ForeignKey('users.id'))
    amount = Column(Numeric)
    description = Column(String)
    date = Column(DateTime, server_default=func.now())
    status = Column(SQLAlchemyEnum(ExpenseStatus))
    
    # Relationships
    household = relationship("Household")
    payer = relationship("User")
    splits = relationship("SharedExpenseSplit", back_populates="expense")

class SharedExpenseSplit(Base):
    __tablename__ = 'shared_expense_splits'
    id = Column(Integer, primary_key=True)
    expense_id = Column(Integer, ForeignKey('shared_expenses.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    amount = Column(Numeric)
    settled = Column(String, default="false")
    
    # Relationships
    expense = relationship("SharedExpense", back_populates="splits")
    user = relationship("User")

class BankAccount(Base):
    __tablename__ = 'bank_accounts'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    household_id = Column(Integer, ForeignKey('households.id'))
    bank_name = Column(String)
    account_type = Column(String)
    account_number = Column(String)
    routing_number = Column(String)
    balance = Column(Numeric)
    
    # Relationships
    user = relationship("User")
    household = relationship("Household")
