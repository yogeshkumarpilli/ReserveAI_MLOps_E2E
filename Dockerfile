# -----------------------------------------------------------------------------
# ML Service Dockerfile
# -----------------------------------------------------------------------------

# Base Image
FROM python:3.12-slim

# Environment Variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/app/.venv \
    PATH="/root/.local/bin:/app/.venv/bin:$PATH" \
    GOOGLE_APPLICATION_CREDENTIALS=/app/gcp-credentials.json

# Set Working Directory
WORKDIR /app

# -----------------------------------------------------------------------------
# System Dependencies
# -----------------------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    # LightGBM dependencies
    libgomp1 \
    # Other tools
    curl \
    # Clean up to reduce image size
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------------------------------------------------------
# Python Package Management Setup
# -----------------------------------------------------------------------------
# Install uv (modern Python dependency manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

# -----------------------------------------------------------------------------
# Application Setup
# -----------------------------------------------------------------------------
# Copy application code
COPY . .

# Create and set up virtual environment
RUN uv venv && \
    uv sync && \
    uv build

# Copy entrypoint script (created by Jenkins pipeline)
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# -----------------------------------------------------------------------------
# Container Configuration
# -----------------------------------------------------------------------------
# Expose API port
EXPOSE 8000

# Set entrypoint script
CMD ["/app/entrypoint.sh"]