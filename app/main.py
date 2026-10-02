from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .database import engine
from . import models

# Initialize the FastAPI application
app = FastAPI(title="PaceCraft")

# Create all database tables based on the models defined
models.Base.metadata.create_all(bind=engine)


# Mount the 'static' directory to serve CSS, JS, and images
# This allows the HTML files to access stylesheets like: /static/css/style.css
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates pointing to the 'templates' directory
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def root(request: Request):
    """
    Root endpoint that renders the main dashboard or landing page.
    """
    # Render the 'index.html' template, passing the request context and any variables
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "title": "Welcome to PaceCraft"}
    )
