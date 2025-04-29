import joblib
import numpy as np
import os
from fastapi import FastAPI, Request, Form, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_swagger_ui_html
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from config.paths_config import MODEL_OUTPUT_PATH
import uvicorn

# Create FastAPI app
app = FastAPI(
    title="Hotel Booking Prediction API",
    description="API for predicting hotel booking cancellations",
    version="1.0.0"
)

# Configure templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Load the pre-trained model
try:
    loaded_model = joblib.load(MODEL_OUTPUT_PATH)
except Exception as e:
    print(f"Error loading model: {e}")
    loaded_model = None

# Define Pydantic models for API input validation
class BookingFeatures(BaseModel):
    lead_time: int = Field(..., description="Number of days between booking and arrival", ge=0)
    no_of_special_request: int = Field(..., description="Number of special requests", ge=0)
    avg_price_per_room: float = Field(..., description="Average price per room", ge=0)
    arrival_month: int = Field(..., description="Month of arrival (1-12)", ge=1, le=12)
    arrival_date: int = Field(..., description="Date of arrival (1-31)", ge=1, le=31)
    market_segment_type: int = Field(..., description="Type of market segment")
    no_of_week_nights: int = Field(..., description="Number of weeknights", ge=0)
    no_of_weekend_nights: int = Field(..., description="Number of weekend nights", ge=0)
    type_of_meal_plan: int = Field(..., description="Type of meal plan")
    room_type_reserved: int = Field(..., description="Type of room reserved")
    
    class Config:
        json_schema_extra = {
            "example": {
                "lead_time": 30,
                "no_of_special_request": 1,
                "avg_price_per_room": 150.0,
                "arrival_month": 6,
                "arrival_date": 15,
                "market_segment_type": 2,
                "no_of_week_nights": 3,
                "no_of_weekend_nights": 2,
                "type_of_meal_plan": 1,
                "room_type_reserved": 2
            }
        }

class PredictionResponse(BaseModel):
    prediction: int
    prediction_text: str
    features: Dict[str, Any]

class ErrorResponse(BaseModel):
    detail: str

# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    error_messages = []
    
    for error in errors:
        field = error["loc"][-1]
        message = error["msg"]
        error_messages.append(f"{field}: {message}")
    
    if request.url.path == "/api/predict":
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": error_messages}
        )
    else:
        error_message = "; ".join(error_messages)
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "status_code": 422, "message": "Validation Error", "detail": error_message}
        )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
    else:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "status_code": exc.status_code, "message": "Error", "detail": exc.detail}
        )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(exc)}
        )
    else:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "status_code": 500,
                "message": "Internal Server Error",
                "detail": "An unexpected error occurred. Please try again later."
            }
        )

# Middleware to check if model is loaded
@app.middleware("http")
async def check_model_loaded(request: Request, call_next):
    if loaded_model is None and "/docs" not in request.url.path and "/openapi.json" not in request.url.path and "/static" not in request.url.path:
        if request.url.path.startswith("/api/"):
            return JSONResponse(
                status_code=503,
                content={"detail": "Model not loaded. Please check server logs."}
            )
        else:
            return templates.TemplateResponse(
                "error.html",
                {
                    "request": request,
                    "status_code": 503,
                    "message": "Service Unavailable",
                    "detail": "The prediction model failed to load. Please contact the administrator."
                }
            )
    response = await call_next(request)
    return response

# API routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "prediction": None})

@app.post("/", response_class=HTMLResponse)
async def predict_form(
    request: Request,
    lead_time: int = Form(...),
    no_of_special_request: int = Form(...),
    avg_price_per_room: float = Form(...),
    arrival_month: int = Form(...),
    arrival_date: int = Form(...),
    market_segment_type: int = Form(...),
    no_of_week_nights: int = Form(...),
    no_of_weekend_nights: int = Form(...),
    type_of_meal_plan: int = Form(...),
    room_type_reserved: int = Form(...)
):
    # Validate inputs
    if arrival_month < 1 or arrival_month > 12:
        return templates.TemplateResponse(
            "index.html", 
            {"request": request, "prediction": None, "error": "Arrival month must be between 1 and 12"}
        )
    
    if arrival_date < 1 or arrival_date > 31:
        return templates.TemplateResponse(
            "index.html", 
            {"request": request, "prediction": None, "error": "Arrival date must be between 1 and 31"}
        )
    
    # Validate date based on month
    days_in_month = {
        1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
        7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
    }
    
    if arrival_date > days_in_month[arrival_month]:
        return templates.TemplateResponse(
            "index.html", 
            {
                "request": request, 
                "prediction": None, 
                "error": f"Invalid date: {arrival_month}/{arrival_date}. Month {arrival_month} has {days_in_month[arrival_month]} days."
            }
        )
    
    features = np.array([[
        lead_time,
        no_of_special_request,
        avg_price_per_room,
        arrival_month,
        arrival_date,
        market_segment_type,
        no_of_week_nights,
        no_of_weekend_nights,
        type_of_meal_plan,
        room_type_reserved
    ]])
    
    try:
        prediction = loaded_model.predict(features)
        prediction_text = "Booking likely to be CANCELLED" if prediction[0] == 1 else "Booking likely to be CONFIRMED"
        
        # Prepare context with all form values to repopulate the form
        context = {
            "request": request, 
            "prediction": int(prediction[0]),
            "prediction_text": prediction_text,
            "form_data": {
                "lead_time": lead_time,
                "no_of_special_request": no_of_special_request,
                "avg_price_per_room": avg_price_per_room,
                "arrival_month": arrival_month,
                "arrival_date": arrival_date,
                "market_segment_type": market_segment_type,
                "no_of_week_nights": no_of_week_nights,
                "no_of_weekend_nights": no_of_weekend_nights,
                "type_of_meal_plan": type_of_meal_plan,
                "room_type_reserved": room_type_reserved
            }
        }
        
        return templates.TemplateResponse("index.html", context)
    
    except Exception as e:
        return templates.TemplateResponse(
            "index.html", 
            {
                "request": request, 
                "prediction": None, 
                "error": f"Prediction error: {str(e)}",
                "form_data": {
                    "lead_time": lead_time,
                    "no_of_special_request": no_of_special_request,
                    "avg_price_per_room": avg_price_per_room,
                    "arrival_month": arrival_month,
                    "arrival_date": arrival_date,
                    "market_segment_type": market_segment_type,
                    "no_of_week_nights": no_of_week_nights,
                    "no_of_weekend_nights": no_of_weekend_nights,
                    "type_of_meal_plan": type_of_meal_plan,
                    "room_type_reserved": room_type_reserved
                }
            }
        )

@app.post("/api/predict", response_model=PredictionResponse)
async def predict_api(booking: BookingFeatures):
    if loaded_model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
        
    features = np.array([[
        booking.lead_time,
        booking.no_of_special_request,
        booking.avg_price_per_room,
        booking.arrival_month,
        booking.arrival_date,
        booking.market_segment_type,
        booking.no_of_week_nights,
        booking.no_of_weekend_nights,
        booking.type_of_meal_plan,
        booking.room_type_reserved
    ]])
    
    try:
        prediction = loaded_model.predict(features)
        prediction_text = "Booking likely to be CANCELLED" if prediction[0] == 1 else "Booking likely to be CONFIRMED"
        
        return {
            "prediction": int(prediction[0]),
            "prediction_text": prediction_text,
            "features": booking.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": loaded_model is not None,
        "version": app.version
    }

# API documentation endpoint
@app.get("/api/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=app.title + " - Swagger UI",
    )

if __name__ == "__main__":
    uvicorn.run("application:app", host="127.0.0.1", port=8000, reload=True)