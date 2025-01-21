import os
from datetime import datetime
from fastapi import FastAPI, File, UploadFile, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import cv2

from app.model import predict_smile
from app.database import create_tables, ClassificationHistory, get_db

# Initialize FastAPI app and templates
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Create database tables on startup
create_tables()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Pydantic Model for the image classification result
class ClassificationResult(BaseModel):
    image_path: str
    result: str

# Function to convert image to JPG format
def convert_to_jpg(file_location: str) -> str:
    """
    Converts the given image file to JPG format.

    Args:
        file_location (str): The path to the image file.

    Returns:
        str: The path to the converted JPG file.
    """
    img = cv2.imread(file_location)
    new_location = file_location.rsplit('.', 1)[0] + '.jpg'
    cv2.imwrite(new_location, img)
    os.remove(file_location)
    return new_location

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Renders the home page.

    Args:
        request (Request): The HTTP request object.

    Returns:
        TemplateResponse: Rendered HTML page.
    """
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/classify", response_class=HTMLResponse)
async def classify(request: Request):
    """
    Renders the classify page for image upload and prediction.

    Args:
        request (Request): The HTTP request object.

    Returns:
        TemplateResponse: Rendered HTML page.
    """
    return templates.TemplateResponse("classify.html", {"request": request})

@app.post("/classify", response_class=HTMLResponse)
async def classify_image(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Handles image upload, prediction, and database logging.

    Args:
        request (Request): The HTTP request object.
        file (UploadFile): The uploaded image file.
        db (Session): Database session dependency.

    Returns:
        TemplateResponse: Rendered HTML page with prediction results.
    """
    try:
        # Save the uploaded file
        file_location = f"static/{file.filename}"
        with open(file_location, "wb") as f:
            f.write(file.file.read())

        # Convert image to JPG format if necessary
        if file.filename.lower().endswith(('.png', '.jpeg')):
            file_location = convert_to_jpg(file_location)

        # Predict using the model
        result = predict_smile(file_location)

        # Log the result in the database
        new_result = ClassificationHistory(
            image_path=file_location,
            predicted_class=result,
            created_at=datetime.utcnow()
        )
        db.add(new_result)
        db.commit()

        # Return the classify page with the result
        return templates.TemplateResponse("classify.html", {
            "request": request,
            "image_path": file_location,
            "result": result
        })
    except Exception as e:
        print(f"Error in classify_image: {e}")
        return HTMLResponse(
            "An error occurred during classification. Please try again.",
            status_code=500
        )

@app.get("/history", response_class=HTMLResponse)
async def history(request: Request, db: Session = Depends(get_db)):
    """
    Displays the classification history from the database.

    Args:
        request (Request): The HTTP request object.
        db (Session): Database session dependency.

    Returns:
        TemplateResponse: Rendered HTML page with classification history.
    """
    try:
        # Query the database for classification history
        history_local = db.query(ClassificationHistory).order_by(ClassificationHistory.created_at.desc()).all()

        # Render the history page with queried data
        return templates.TemplateResponse("history.html", {
            "request": request,
            "history": history_local
        })
    except Exception as e:
        print(f"Error in history endpoint: {e}")
        return templates.TemplateResponse("history.html", {
            "request": request,
            "error": "An error occurred while fetching the history."
        })
