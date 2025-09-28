FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    cmake \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --no-cache-dir \
    feast[postgres]==0.47.0 \
    psycopg2-binary \
    pandas \
    numpy

# Copy test script
COPY test_feast_timescale.py .

# Run as non-root user
RUN useradd -m -u 1000 testuser
USER testuser

# Set working directory to user home
WORKDIR /home/testuser

CMD ["python", "/app/test_feast_timescale.py"]