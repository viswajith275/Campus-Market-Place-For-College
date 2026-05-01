# Runtime stage
FROM python:3.14-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client libmagic1\
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

# Copy lock file and pyproject.toml
COPY uv.lock pyproject.toml ./

# Create virtual environment and install all dependencies
RUN python -m venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
RUN uv sync --frozen

# Copy application code
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./

ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/docs')" || exit 1

# Run alembic migrations and then uvicorn
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000"]
