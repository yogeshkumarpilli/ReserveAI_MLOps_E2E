import pytest
import os
import sys
from pathlib import Path
import joblib
import numpy as np
from fastapi.testclient import TestClient
from application import app

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def sample_model(tmp_path):
    # Create a simple mock model for testing
    class MockModel:
        def predict(self, X):
            return np.array([0, 1, 0])
    
    model_path = tmp_path / "mock_model.joblib"
    model = MockModel()
    joblib.dump(model, model_path)
    return model_path

@pytest.fixture
def valid_prediction_data():
    return {
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

@pytest.fixture
def invalid_prediction_data():
    return {
        "lead_time": -1,  # Invalid negative value
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