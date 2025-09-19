FROM --platform=linux/arm64 python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Environment variables with defaults
ENV FORECAST_HORIZON=3
ENV NUM_FEATURES=12
ENV HOST=0.0.0.0
ENV PORT=8000

EXPOSE 8000
CMD ["python", "main.py"]