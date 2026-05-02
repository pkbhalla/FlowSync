FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app
USER appuser

ENV FLASK_ENV=production
ENV PORT=8080

EXPOSE 8080

CMD ["gunicorn", "--worker-class", "gevent", "--workers", "1", "--worker-connections", "1000", "--bind", "0.0.0.0:8080", "run:app"]
