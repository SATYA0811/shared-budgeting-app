from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

# Database URL - using SQLite for development
DATABASE_URL = "sqlite:///./dev.db"

# Create engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Database dependency for FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)