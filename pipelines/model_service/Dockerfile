FROM --platform=linux/arm64 python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Environment variables with defaults
ENV MODEL_NAME=linear_regression
ENV HOST=0.0.0.0
ENV PORT=8000

EXPOSE 8000
CMD ["python", "main.py"]