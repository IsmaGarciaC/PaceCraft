from fastapi import FastAPI, Request, Form, Depends, status, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from .database import engine, get_db
from . import models, auth
from .calculations import calculate_pace, format_pace, predict_time, format_time

# Initialize the FastAPI application
app = FastAPI(title="PaceCraft")

# Create all database tables based on the models defined
models.Base.metadata.create_all(bind=engine)

# Mount the 'static' directory to serve CSS, JS, and images
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Register custom Jinja filters
templates.env.filters["format_pace"] = format_pace
templates.env.filters["format_time"] = format_time

# ---------------------------------------------------------
# UI Routes
# ---------------------------------------------------------

@app.get("/")
async def root(request: Request, user: models.User = Depends(auth.get_current_user_from_cookie)):
    """
    Root endpoint. Shows user dashboard if authenticated.
    """
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "title": "Dashboard", "user": user}
    )

@app.get("/add-run")
async def add_run_page(request: Request, user: models.User = Depends(auth.get_current_user_from_cookie)):
    """Displays the HTML form to log a new run."""
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("add_run.html", {"request": request, "title": "Log a Run", "user": user})

@app.post("/add-run")
async def add_run(
    request: Request,
    title: str = Form(...),
    distance_km: float = Form(...),
    time_minutes: float = Form(...),
    user: models.User = Depends(auth.get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    """Processes the form submission, calculates pace, and saves the run to the database."""
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    # Use business logic module to calculate pace
    pace = calculate_pace(distance_km=distance_km, time_minutes=time_minutes)
    
    # Create and save the run linked to the current user
    new_run = models.Run(
        title=title,
        distance_km=distance_km,
        time_minutes=time_minutes,
        pace=pace,
        user_id=user.id
    )
    db.add(new_run)
    db.commit()
    
    # Redirect back to dashboard to see the new run
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

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
    existing_user = db.query(models.User).filter(models.User.username == username).first()
    if existing_user:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Username already taken."})
    
    hashed_pw = auth.get_password_hash(password)
    new_user = models.User(username=username, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    
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
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not auth.verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid username or password."})
    
    access_token = auth.create_access_token(data={"sub": user.username})
    
    redirect = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    redirect.set_cookie(
        key="access_token", 
        value=f"Bearer {access_token}", 
        httponly=True, 
        secure=False, 
        max_age=auth.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    return redirect

@app.get("/logout")
async def logout():
    redirect = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    redirect.delete_cookie(key="access_token")
    return redirect

@app.get("/predictions")
async def predictions_page(request: Request, user: models.User = Depends(auth.get_current_user_from_cookie)):
    """Displays race projections based on the user's most recent run."""
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    # Get the most recent run to use as baseline
    latest_run = max(user.runs, key=lambda r: r.date, default=None) if user.runs else None
    
    projections = None
    if latest_run:
        projections = {
            "5K": predict_time(latest_run.time_minutes, latest_run.distance_km, 5.0),
            "10K": predict_time(latest_run.time_minutes, latest_run.distance_km, 10.0),
            "Half Marathon": predict_time(latest_run.time_minutes, latest_run.distance_km, 21.0975)
        }
        
    return templates.TemplateResponse(
        "predictions.html", 
        {
            "request": request, 
            "title": "Race Projections", 
            "user": user, 
            "baseline_run": latest_run,
            "projections": projections
        }
    )

