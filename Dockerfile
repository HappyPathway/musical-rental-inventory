FROM python:3.10-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV GS_BUCKET_NAME=roknsound-music-rental-inventory
ENV GS_PROJECT_ID=happypathway-1522441039906
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/gcp-service-account-key.json

# Accept build argument for migrations only mode
ARG MIGRATIONS_ONLY=0
ENV MIGRATIONS_ONLY=${MIGRATIONS_ONLY}

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project (excluding unnecessary files)
COPY . .

# Remove QR code files and other unnecessary files to reduce image size
RUN find . -path "*/generated_qrcodes/*" -type f -delete && \
    find . -path "*/test-screenshots/*" -type f -delete && \
    find . -path "*/pyc/*" -type f -delete && \
    find . -name "*.pyc" -delete && \
    find . -name "__pycache__" -type d -exec rm -rf {} +

# Collect static files
RUN python manage.py collectstatic --noinput

# Create entrypoint script that can handle both migrations and regular startup
RUN echo '#!/bin/bash\n\
if [ "$MIGRATIONS_ONLY" = "1" ] || [ "$MIGRATE_ONLY" = "1" ]; then\n\
  echo "Running migrations only..."\n\
  python manage.py migrate --noinput\n\
  echo "Migrations complete."\n\
else\n\
  # Run migrations and start the server\n\
  python manage.py migrate --noinput\n\
  gunicorn --bind :$PORT --workers 2 --threads 8 --timeout 0 --log-level debug music_rental.wsgi:application\n\
fi' > /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

# Use entrypoint script
CMD ["/app/entrypoint.sh"]