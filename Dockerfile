# Base operating environment: Official lightweight Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables for optimized container execution
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000

# Create dedicated application directory
WORKDIR /app

# Install security updates and curl for healthcheck probe
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Layer Caching: Copy only requirements first to optimize build times
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy complete project source code into container
COPY . .

# Security Best Practice: Run application as non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose internal application port
EXPOSE 5000

# Healthcheck probe to monitor container health via /api/health
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/api/health || exit 1

# Launch the production application
CMD ["python", "run.py"]
