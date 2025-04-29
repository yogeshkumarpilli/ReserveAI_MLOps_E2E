import pytest
from fastapi.testclient import TestClient
from application import app
import joblib
import numpy as np
from pathlib import Path
import sys

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

client = TestClient(app)

def test_home_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "model_loaded" in data
    assert "version" in data

def test_predict_api_valid_data():
    test_data = {
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
    
    response = client.post("/api/predict", json=test_data)
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "prediction_text" in data
    assert "features" in data
    assert data["prediction"] in [0, 1]

def test_predict_api_invalid_data():
    test_data = {
        "lead_time": -1,  # Invalid negative value
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
    
    response = client.post("/api/predict", json=test_data)
    assert response.status_code == 422  # Validation error

def test_predict_form_valid_data():
    form_data = {
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
    
    response = client.post("/", data=form_data)
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_predict_form_invalid_data():
    form_data = {
        "lead_time": 30,
        "no_of_special_request": 1,
        "avg_price_per_room": 150.0,
        "arrival_month": 13,  # Invalid month
        "arrival_date": 15,
        "market_segment_type": 2,
        "no_of_week_nights": 3,
        "no_of_weekend_nights": 2,
        "type_of_meal_plan": 1,
        "room_type_reserved": 2
    }
    
    response = client.post("/", data=form_data)
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Arrival month must be between 1 and 12" in response.text

def test_api_docs_endpoint():
    response = client.get("/api/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_openapi_schema():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]
    schema = response.json()
    assert "openapi" in schema
    assert "info" in schema
    assert "paths" in schema

def test_static_files():
    response = client.get("/static/style.css")
    assert response.status_code == 200
    assert "text/css" in response.headers["content-type"]

def test_error_handling():
    # Test with invalid endpoint
    response = client.get("/invalid-endpoint")
    assert response.status_code == 404

    # Test with invalid method
    response = client.put("/")
    assert response.status_code == 405  # Method Not Allowed 