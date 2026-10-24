# ---------- Stage 1: install dependencies ----------
FROM python:3.12-slim AS builder

WORKDIR /build
COPY requirements.txt .

# Install packages into a separate folder so only they are copied to the final image
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ---------- Stage 2: minimal runtime image ----------
FROM python:3.12-slim

# OCI metadata labels (shown in registries like GHCR)
LABEL org.opencontainers.image.title="CloudPulse" \
      org.opencontainers.image.description="Production-grade Kubernetes platform on Google Cloud" \
      org.opencontainers.image.authors="Hina Naseer"

# Python runtime best practices: no .pyc files, unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_ENV=production

# Create a non-root user for security
RUN groupadd --system --gid 10001 app && useradd --system --uid 10001 --gid app --no-create-home app

WORKDIR /app

# Copy installed packages from the builder stage
COPY --from=builder /install /usr/local

# Copy only the application code (venv and other files stay out)
COPY --chown=app:app app.py .
COPY --chown=app:app templates/ templates/

# Run as non-root user
USER 10001:10001

EXPOSE 8080

# Container-level health check using the /health endpoint
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

# Production server: Gunicorn with 2 workers, access logs to stdout
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "4", "--access-logfile", "-", "app:app"]
