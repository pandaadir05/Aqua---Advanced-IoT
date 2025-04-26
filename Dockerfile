# Use Python 3.9 as the base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies including Nmap
RUN apt-get update && apt-get install -y \
    nmap \
    libpcap-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install the application
RUN pip install -e .

# Expose ports for web UI and API
EXPOSE 8000

# Create volume for data persistence
VOLUME /app/data

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Command to run
CMD ["python", "-m", "aqua.web.app"]
