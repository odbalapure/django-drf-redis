# Use official Python image
FROM python:3.13.2-alpine3.21

# Set working directory
WORKDIR /app

# Copy project files
COPY requirements.txt .

# Install dependencies
# pip caches pacakge files under ~/.cache/pip
# Avoid leaving behind temporary files
# Since the image won't reuse the cache
RUN pip install --no-cache-dir -r requirements.txt