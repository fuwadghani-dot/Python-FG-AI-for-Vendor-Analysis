# Minimal Dockerfile for running the FastAPI service
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# system deps for Pillow / openpyxl etc
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libssl-dev libffi-dev libxml2 libxml2-dev libxslt1-dev libjpeg-dev zlib1g-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s CMD curl -f http://127.0.0.1:8000/status || exit 1

CMD ["uvicorn", "scripts.service:app", "--host", "0.0.0.0", "--port", "8000"]
