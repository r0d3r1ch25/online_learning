FROM python:3.11-alpine

# Install only required packages
RUN pip install --no-cache-dir requests

# Copy pipeline script
COPY pipeline.py /app/pipeline.py

WORKDIR /app

# Run the pipeline
CMD ["python", "pipeline.py"]