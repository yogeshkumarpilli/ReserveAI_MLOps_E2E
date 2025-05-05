#!/bin/bash
set -e

# Check if we need to train the model
if [ -f "$GOOGLE_APPLICATION_CREDENTIALS" ] || [ -f "/app/data/Hotel_Reservation.csv" ]; then
    echo "Starting model training..."
    python /app/pipeline/training.py
else
    echo "Skipping model training - no credentials or sample data found"
    echo "WARNING: Application may not work correctly without a trained model"
fi

# Run the application
echo "Starting the application..."
exec python /app/application.py