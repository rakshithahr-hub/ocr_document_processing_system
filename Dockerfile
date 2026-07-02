# Use a Python base image
FROM python:3.9-slim

# Install Tesseract and other system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p uploads outputs temp
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]