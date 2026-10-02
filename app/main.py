from fastapi import FastAPI, Request, Form, Depends, status, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from .database import engine, get_db
from . import models, auth

# Initialize the FastAPI application
app = FastAPI(title="PaceCraft")

# Create all database tables based on the models defined
models.Base.metadata.create_all(bind=engine)

# Mount the 'static' directory to serve CSS, JS, and images
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

# ---------------------------------------------------------
# UI Routes
# ---------------------------------------------------------

@app.get("/")
async def root(request: Request, user: models.User = Depends(auth.get_current_user_from_cookie)):
    """
    Root endpoint. If user is not authenticated, redirect to login.
    """
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "title": "Dashboard", "user": user}
    )

@app.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "title": "Register"})

@app.post("/register")
async def register(
    request: Request, 
    username: str = Form(...), 
    password: str = Form(...), 
    db: Session = Depends(get_db)
):
    # Check if username exists
    existing_user = db.query(models.User).filter(models.User.username == username).first()
    if existing_user:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Username already taken."})
    
    # Hash password and save new user
    hashed_pw = auth.get_password_hash(password)
    new_user = models.User(username=username, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    
    # Redirect to login
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)


@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "title": "Login"})

@app.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Verify user exists and password is correct
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not auth.verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid username or password."})
    
    # Generate JWT token
    access_token = auth.create_access_token(data={"sub": user.username})
    
    # Create redirect response and set the HttpOnly cookie
    redirect = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    redirect.set_cookie(
        key="access_token", 
        value=f"Bearer {access_token}", 
        httponly=True, 
        secure=False, # Set to True if using HTTPS
        max_age=auth.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    return redirect

@app.get("/logout")
async def logout():
    """
    Clears the JWT cookie and redirects to login.
    """
    redirect = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    redirect.delete_cookie(key="access_token")
    return redirect
