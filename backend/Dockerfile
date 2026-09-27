FROM python:3.11-slim

# Install system dependencies for PostgreSQL, OpenCV, PDF handling, and Multilingual Indic OCR
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-tel \
    tesseract-ocr-hin \
    tesseract-ocr-tam \
    tesseract-ocr-kan \
    tesseract-ocr-mar \
    tesseract-ocr-guj \
    tesseract-ocr-ben \
    tesseract-ocr-ori \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create volume directories
RUN mkdir -p /app/uploads /app/preprocessed

EXPOSE 8000

ENV PORT=8000
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
