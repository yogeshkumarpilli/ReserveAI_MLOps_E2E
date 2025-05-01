# First, build the application in the `/app` directory.

# Use a lightweight Python image
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

#FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=0
ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=UTF-8 \
    PYTHONDONTWRITEBYTECODE=1
ENV PATH="/root/.local/bin/:$PATH"

WORKDIR /app
# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

ADD . /app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

    #FROM python:3.12-slim

    # Copy the environment, but not the source code
   # COPY --from=builder --chown=app:app /app/.venv /app/.venv

# Install system dependencies required by LightGBM and UV
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app


# Copy Python installation and virtual environment from builder
# 3. Copy from builder (corrected - no circular reference)
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=ghcr.io/astral-sh/uv:0.7.2 /uv /uvx /bin/
COPY . .

# Expose the port that fastapi will run on
EXPOSE 8000
# Install application in editable mode
#RUN uv pip install -e .
RUN uv sync --locked
# Training the model before running the application
RUN python pipeline/training.py



# Command to run the app
CMD ["uv","run" "application:app"]