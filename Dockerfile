# Use a lightweight Python image
FROM python:slim

# Set environment variables to prevent Python from writing .pyc files & Ensure Python output is not buffered
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 
    #PATH="/root/.local/bin/:$PATH"

# Set the working directory
WORKDIR /app

# The installer requires curl (and certificates) to download the release archive
#RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates

# Download the latest installer
#ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
#RUN sh /uv-installer.sh && rm /uv-installer.sh


# Install system dependencies required by LightGBM and UV
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* 


    # Copy the application code
COPY . .

# Install the package in editable mode

RUN uv sync --locked \
    uv build

# Training the model before running the application

RUN uv run pipeline/training.py

# Expose the port that fastapi will run on
EXPOSE 8000

# Command to run the app
CMD ["python", "application.py"]