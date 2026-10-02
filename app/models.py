from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base

class User(Base):
    """
    Database model representing a registered user.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Relationship linking the User to multiple Runs
    runs = relationship("Run", back_populates="owner")


class Run(Base):
    """
    Database model representing a running session (training).
    """
    __tablename__ = "runs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, default="Training Run")
    distance_km = Column(Float, nullable=False)
    time_minutes = Column(Float, nullable=False)
    pace = Column(Float, nullable=False)  # Stored as min/km
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    user_id = Column(Integer, ForeignKey("users.id"))

    # Relationship linking the Run back to its User owner
    owner = relationship("User", back_populates="runs")
