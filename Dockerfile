FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends tesseract-ocr poppler-utils fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
ENV DATA_DIR=/tmp/data PORT=10000 PYTHONUNBUFFERED=1
RUN mkdir -p /tmp/data
# One worker: SQLite + in-memory login lockout; threads handle concurrency. Long timeout for OCR/PDF.
CMD gunicorn app:app --bind 0.0.0.0:${PORT} --workers 1 --threads 4 --timeout 120
