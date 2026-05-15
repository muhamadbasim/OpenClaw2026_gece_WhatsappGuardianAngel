# WhatsApp Scam Guardian - Dockerfile
FROM python:3.11-slim

# Create non-root user for security
RUN groupadd -r guardian && useradd -r -g guardian -d /app -s /sbin/nologin guardian

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies (no cache to reduce image size)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project source code
COPY . .

# Create /data directory for SQLite persistence and set ownership
RUN mkdir -p /data && chown -R guardian:guardian /app /data

# Expose health-check endpoint port
EXPOSE 8080

# Switch to non-root user
USER guardian

# Set entrypoint to run the application
ENTRYPOINT ["python", "src/main.py"]
