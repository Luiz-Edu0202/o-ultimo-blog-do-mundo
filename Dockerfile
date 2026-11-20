# =============================================================================
# O Último Blog do Mundo — Multi-stage Dockerfile
# =============================================================================
# Stage 1 (builder): installs build-time dependencies and Python packages.
# Stage 2 (final):   lean runtime image with non-root user, collectstatic baked
#                    in, and Gunicorn as entrypoint.
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1 — builder
# -----------------------------------------------------------------------------
FROM python:3.15-slim AS builder

# Install OS-level build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Copy only requirements first to leverage Docker layer cache
COPY requirements/ requirements/

# Install production Python dependencies into an isolated prefix
RUN pip install --upgrade pip \
    && pip install --prefix=/install --no-cache-dir -r requirements/production.txt


# -----------------------------------------------------------------------------
# Stage 2 — final
# -----------------------------------------------------------------------------
FROM python:3.15-slim AS final

# Install runtime OS dependencies (libpq for psycopg)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Create non-root user
RUN groupadd --gid 1000 appgroup \
    && useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

WORKDIR /app

# Copy project source
COPY . .

# Dummy SECRET_KEY for collectstatic — NEVER used at runtime.
# Real SECRET_KEY must be supplied via environment variable.
ARG SECRET_KEY=dummy-build-secret-key-not-used-at-runtime

# Collect static files (WhiteNoise serves them at runtime, no web server needed)
RUN DJANGO_SETTINGS_MODULE=config.settings.production \
    SECRET_KEY=${SECRET_KEY} \
    DEBUG=False \
    ALLOWED_HOSTS=* \
    DATABASE_URL=sqlite:////dev/null \
    REDIS_URL=redis://localhost:6379/0 \
    python manage.py collectstatic --noinput --clear

# Switch to non-root user AFTER collectstatic (needs write access to staticfiles/)
RUN chown -R appuser:appgroup /app
USER appuser

# Expose the application port
EXPOSE 8000

# Health check — calls the /healthz endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/healthz')" || exit 1

# Gunicorn entrypoint — configure via GUNICORN_WORKERS and GUNICORN_TIMEOUT env vars
ENV DJANGO_SETTINGS_MODULE=config.settings.production
ENV GUNICORN_WORKERS=2
ENV GUNICORN_TIMEOUT=120
ENV PORT=8000

CMD ["sh", "-c", \
    "python manage.py migrate --noinput && \
     gunicorn config.wsgi:application \
       --bind 0.0.0.0:${PORT} \
       --workers ${GUNICORN_WORKERS} \
       --timeout ${GUNICORN_TIMEOUT} \
       --log-file - \
       --access-logfile -"]
