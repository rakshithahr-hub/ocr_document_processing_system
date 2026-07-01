#!/usr/bin/env bash
echo "🚀 Starting build process..."

# Install system dependencies for PDF processing
echo "📦 Installing poppler and Tesseract..."
apt-get update
apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    # ... other tesseract language packages