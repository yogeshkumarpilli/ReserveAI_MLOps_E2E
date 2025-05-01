# Use a lightweight Python image
FROM python:slim

# Set environment variables to prevent Python from writing .pyc files & Ensure Python output is not buffered
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install system dependencies required by LightGBM
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

    # Copy the application code
COPY . .

# Install the package in editable mode

RUN uv build

# Training the model before running the application

RUN uv run pipeline/training_pipeline.py

# Expose the port that fastapi will run on
EXPOSE 8000

# Command to run the app
CMD ["python", "application.py"]