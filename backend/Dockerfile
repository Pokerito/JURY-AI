# ── Stage 1: Build dependencies ──────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy dependency spec and install
COPY pyproject.toml ./
RUN pip install --no-cache-dir --prefix=/install .

# ── Stage 2: Production image ───────────────────────────────────────────────
FROM python:3.12-slim AS runtime

WORKDIR /app

# Install only runtime system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 curl && \
    rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY alembic/ ./alembic/
COPY alembic.ini ./
COPY app/ ./app/
COPY scripts/ ./scripts/

# Create data directories
RUN mkdir -p /app/data/chroma /app/data/uploads

# Non-root user for security
RUN groupadd -r juryai && useradd -r -g juryai juryai && \
    chown -R juryai:juryai /app
USER juryai

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

# Run with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
