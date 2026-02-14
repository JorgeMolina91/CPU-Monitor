# Lightweight base image
FROM python:3.11-slim

# Environment variables to optimize Python in Docker
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Working directory
WORKDIR /app

# Install system dependencies required for psutil
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port used by Flask/Gunicorn
EXPOSE 5000

# Command to run with Gunicorn (Production)
# 'app:app' assumes your file is named app.py and the variable is app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]