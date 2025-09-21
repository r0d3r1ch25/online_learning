FROM python:3.11-alpine

# Create non-root user
RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup

# Copy requirements and install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy pipeline script
COPY pipeline.py /app/pipeline.py

# Change ownership to non-root user
RUN chown -R appuser:appgroup /app

WORKDIR /app

# Switch to non-root user
USER appuser

# Run the pipeline
CMD ["python", "pipeline.py"]