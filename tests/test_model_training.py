import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os
import joblib
from src.model_training import ModelTraining
from src.custom_exception import CustomException

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

# Test data setup
@pytest.fixture
def sample_data():
    return pd.DataFrame({
        'lead_time': [10, 20, 30],
        'no_of_special_request': [1, 2, 3],
        'avg_price_per_room': [100.0, 150.0, 200.0],
        'arrival_month': [1, 2, 3],
        'arrival_date': [1, 15, 30],
        'market_segment_type': [1, 2, 3],
        'no_of_week_nights': [2, 3, 4],
        'no_of_weekend_nights': [1, 2, 3],
        'type_of_meal_plan': [1, 2, 3],
        'room_type_reserved': [1, 2, 3],
        'booking_status': [0, 1, 0]
    })

@pytest.fixture
def model_trainer(tmp_path):
    train_path = tmp_path / "train.csv"
    test_path = tmp_path / "test.csv"
    model_output_path = tmp_path / "model.joblib"
    return ModelTraining(train_path, test_path, model_output_path)

def test_load_and_split_data(model_trainer, sample_data, tmp_path):
    # Save sample data to temporary files
    train_path = tmp_path / "train.csv"
    test_path = tmp_path / "test.csv"
    sample_data.to_csv(train_path, index=False)
    sample_data.to_csv(test_path, index=False)
    
    # Test the method
    X_train, y_train, X_test, y_test = model_trainer.load_and_split_data()
    
    # Assertions
    assert isinstance(X_train, pd.DataFrame)
    assert isinstance(y_train, pd.Series)
    assert isinstance(X_test, pd.DataFrame)
    assert isinstance(y_test, pd.Series)
    assert "booking_status" not in X_train.columns
    assert "booking_status" not in X_test.columns
    assert len(X_train) == len(y_train)
    assert len(X_test) == len(y_test)

def test_train_lgbm(model_trainer, sample_data):
    # Prepare data
    X = sample_data.drop(columns=["booking_status"])
    y = sample_data["booking_status"]
    
    # Test the method
    model = model_trainer.train_lgbm(X, y)
    
    # Assertions
    assert model is not None
    assert hasattr(model, 'predict')
    assert hasattr(model, 'fit')

def test_evaluate_model(model_trainer, sample_data):
    # Prepare data
    X = sample_data.drop(columns=["booking_status"])
    y = sample_data["booking_status"]
    
    # Train a model
    model = model_trainer.train_lgbm(X, y)
    
    # Test the method
    metrics = model_trainer.evaluate_model(model, X, y)
    
    # Assertions
    assert isinstance(metrics, dict)
    assert "accuracy" in metrics
    assert "precison" in metrics
    assert "recall" in metrics
    assert "f1" in metrics
    assert all(0 <= value <= 1 for value in metrics.values())

def test_save_model(model_trainer, sample_data, tmp_path):
    # Prepare data and train model
    X = sample_data.drop(columns=["booking_status"])
    y = sample_data["booking_status"]
    model = model_trainer.train_lgbm(X, y)
    
    # Test the method
    model_trainer.save_model(model)
    
    # Assertions
    assert os.path.exists(model_trainer.model_output_path)
    loaded_model = joblib.load(model_trainer.model_output_path)
    assert loaded_model is not None

def test_test_model(model_trainer, sample_data, tmp_path):
    # Save sample data to temporary files
    train_path = tmp_path / "train.csv"
    test_path = tmp_path / "test.csv"
    sample_data.to_csv(train_path, index=False)
    sample_data.to_csv(test_path, index=False)
    
    # Test the method
    model_trainer.test_model()
    
    # Assertions
    assert os.path.exists(model_trainer.model_output_path)

def test_run_method(model_trainer, sample_data, tmp_path):
    # Save sample data to temporary files
    train_path = tmp_path / "train.csv"
    test_path = tmp_path / "test.csv"
    sample_data.to_csv(train_path, index=False)
    sample_data.to_csv(test_path, index=False)
    
    # Test the method
    model_trainer.run()
    
    # Assertions
    assert os.path.exists(model_trainer.model_output_path)

def test_invalid_data_handling(model_trainer, tmp_path):
    # Create empty files
    train_path = tmp_path / "train.csv"
    test_path = tmp_path / "test.csv"
    train_path.touch()
    test_path.touch()
    
    # Test error handling
    with pytest.raises(CustomException) as exc_info:
        model_trainer.load_and_split_data()
    
    error_message = str(exc_info.value)
    assert "Failed to load data" in error_message 