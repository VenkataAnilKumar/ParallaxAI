FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Install dependencies first (cached layer)
COPY pyproject.toml .
RUN uv sync --frozen --no-dev

# Copy application code
COPY . .

# Default command (overridden by docker-compose)
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
