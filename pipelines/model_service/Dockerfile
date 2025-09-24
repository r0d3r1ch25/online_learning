FROM --platform=linux/arm64 python:3.11-slim

# Create non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Change ownership to non-root user
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Environment variables with defaults
ENV MODEL_NAME=linear_regression
ENV HOST=0.0.0.0
ENV PORT=8000

EXPOSE 8000
CMD ["python", "main.py"]