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


# Train the model before running the application
RUN uv run pipeline/training.py

# Handle GCP credentials
#ARG GCP_KEY_JSON
#ENV GOOGLE_APPLICATION_CREDENTIALS=/app/gcp-credentials.json
#RUN if [ -n "$GCP_KEY_JSON" ]; then \
#       echo "$GCP_KEY_JSON" > /app/gcp-credentials.json && \
#       echo "✓ GCP credentials injected"; \
#    fi

# Debug GCP permissions if credentials exist
#RUN if [ -f "$GOOGLE_APPLICATION_CREDENTIALS" ]; then \
#        echo "GCP credentials found, installing gcloud for debugging" && \
#        apt-get update && apt-get install -y curl apt-transport-https ca-certificates gnupg && \
#        echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
#        curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - && \
#        apt-get update && apt-get install -y google-cloud-sdk && \
#        gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS && \
#        echo "Service account info:" && \
#        gcloud auth list && \
#        echo "Testing GCS access:" && \
#        gsutil ls gs://your-bucket-name 2>&1 || echo "GCS access failed"; \
#    else \
#        echo "No GCP credentials found. Model training will be done at runtime."; \
#    fi

# Add an entry point script that decides whether to train or not
#COPY entrypoint.sh /app/
#RUN chmod +x /app/entrypoint.sh

# Final cleanup (GCP creds)
#RUN rm -f /app/gcp-credentials.json || true

# Expose FastAPI port
EXPOSE 8000

# Command to run the app
CMD ["uv","run", "application.py"]