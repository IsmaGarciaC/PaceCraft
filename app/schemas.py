from pydantic import BaseModel

# -----------------
# User Schemas
# -----------------
class UserCreate(BaseModel):
    """
    Schema for validating user creation data.
    """
    username: str
    password: str

class UserResponse(BaseModel):
    """
    Schema for returning user data (excluding passwords!).
    """
    id: int
    username: str

    class Config:
        from_attributes = True

# -----------------
# Run Schemas (For future Phase 4)
# -----------------
class RunBase(BaseModel):
    title: str
    distance_km: float
    time_minutes: float

class RunResponse(RunBase):
    id: int
    pace: float
    user_id: int

    class Config:
        from_attributes = True
