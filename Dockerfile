# Use a lightweight Python base image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies required by LightGBM and other tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install uv (modern Python dependency manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

ENV PATH="/root/.local/bin:${PATH}"

# Copy application code
COPY . .

# Set up virtual environment
RUN uv venv

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies and build
RUN uv sync && uv build

# Optional: Remove GCP credentials if present
#ARG GCP_KEY_JSON
#ENV GOOGLE_APPLICATION_CREDENTIALS=/app/gcp-credentials.json
#RUN if [ -n "$GCP_KEY_JSON" ]; then \
      #  echo "$GCP_KEY_JSON" > /app/gcp-credentials.json && \
      #  echo "✓ GCP credentials injected"; \
    #fi

# Final cleanup (GCP creds)
#RUN rm -f /app/gcp-credentials.json || true

# Expose FastAPI port
EXPOSE 8000

# Run the application (assumes uvicorn usage)
CMD ["uvicorn","application:app", "--host", "0.0.0.0", "--port", "8000"]
