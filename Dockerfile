# Use a lightweight Python image
FROM python:3.12-slim

# Set environment variables to prevent Python from writing .pyc files & Ensure Python output is not buffered
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install system dependencies required by LightGBM
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Copy the application code
COPY . .

ENV PATH="$HOME/.local/bin:$PATH"

# Install the package in editable mode using uv
RUN uv sync
RUN uv build

# Train the model before running the application
RUN python pipeline/training_pipeline.py

# Expose the port that Flask will run on
EXPOSE 5000

# Command to run the app
CMD ["python", "application.py"]