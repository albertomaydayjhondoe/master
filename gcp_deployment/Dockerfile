# Meta Ads Docker Configuration
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=8000

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
COPY requirements-prod.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements-prod.txt

# Install additional production dependencies
RUN pip install --no-cache-dir \
    google-cloud-storage \
    google-cloud-pubsub \
    google-cloud-secret-manager \
    google-cloud-monitoring \
    google-cloud-logging \
    psycopg2-binary \
    facebook-business \
    uvicorn[standard] \
    gunicorn

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/models data/logs config/secrets

# Set up proper permissions
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# Expose port
EXPOSE $PORT

# Production startup command
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]