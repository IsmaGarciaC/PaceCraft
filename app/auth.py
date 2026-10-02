from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Request, Depends
from sqlalchemy.orm import Session
from .database import get_db
from . import models

# In a real app, hide this in a .env file!
SECRET_KEY = "CS50_PACECRAFT_SUPER_SECRET_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 1 week

# Configures passlib to use the bcrypt algorithm for hashing passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    """Checks if a plain text password matches the hashed version."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Generates a secure hash for a password."""
    return pwd_context.hash(password)

def create_access_token(data: dict):
    """Creates a JWT token with an expiration date."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user_from_cookie(request: Request, db: Session = Depends(get_db)):
    """
    Custom dependency to extract the JWT from the HttpOnly cookie, 
    decode it, and retrieve the user from the database.
    """
    token = request.cookies.get("access_token")
    if not token:
        return None
    
    # Strip the "Bearer " prefix if we prepended it
    if token.startswith("Bearer "):
        token = token.split(" ")[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None
        
    user = db.query(models.User).filter(models.User.username == username).first()
    return user
