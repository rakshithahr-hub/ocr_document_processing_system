FROM python:3.10-slim

# Prevent Python from buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install OCR dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-kan \
    poppler-utils \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /app

# Copy backend files
COPY backend/ .

# Install Python packages
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Render provides PORT environment variable
ENV PORT=10000

EXPOSE 10000

CMD ["gunicorn","--bind","0.0.0.0:10000","--workers","1","--timeout","600","app:app"]