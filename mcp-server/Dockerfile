# Use a slim, secure base image
FROM python:3.11-slim

# Install system diagnostic tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    iproute2 \
    iputils-ping \
    dnsutils \
    procps \
    docker.io \
    && curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" \
    && chmod +x kubectl \
    && mv kubectl /usr/local/bin/ \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Add a non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser
WORKDIR /app

# Install dependencies before adding code to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application logic
COPY server.py .
COPY guardrails.py .

# Switch to the non-root user
USER appuser

# Environment variables for execution
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Expose the server's port
EXPOSE 8080

# Command to start the MCP server
CMD ["python", "server.py"]
