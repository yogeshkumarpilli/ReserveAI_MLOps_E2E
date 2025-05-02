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
RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
    && echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

ENV PATH="/root/.local/bin:${PATH}"

# Copy the application code
COPY . .

# Install the package in editable mode using uv
RUN uv venv

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN uv sync
RUN uv build

# Debug: Verify final directory structure
RUN echo "→ Final directory structure:" \
    && ls -la \
    && echo "✓ All files copied"

# Train the model before running the application
RUN uv run pipeline/training.py

# Expose the port that FastAPI will run on
EXPOSE 8000

# Command to run the app
CMD ["uv","run", "application.py"]