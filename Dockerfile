# First, build the application in the `/app` directory.
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Disable Python downloads, because we want to use the system interpreter
# across both images
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Copy only dependency files first to leverage caching
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Copy the rest of the application code
COPY . .

# Install project in development mode
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Use a lightweight Python image for the final stage
FROM python:3.12-slim

# Install system dependencies required by LightGBM
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python installation and virtual environment from builder
COPY --from=builder /app /app
COPY --from=builder /usr/local/bin/uv /usr/local/bin/uv
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Expose the port that FastAPI will run on
EXPOSE 8000

# Train the model before starting the application
RUN uv run pipeline/training.py

# Command to run the app
CMD ["uv", "run", "application.py"]