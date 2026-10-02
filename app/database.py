from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite connection string. Will create 'pacecraft.db' in the root directory.
SQLALCHEMY_DATABASE_URL = "sqlite:///./pacecraft.db"

# 'check_same_thread': False is required for SQLite in FastAPI to allow concurrent requests
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# SessionLocal class will act as a database session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our SQLAlchemy models to inherit from
Base = declarative_base()

def get_db():
    """
    Dependency function to get a database session for each API request.
    Ensures the connection is safely closed after the request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
