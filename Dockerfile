FROM python:3.14-slim-bookworm

RUN apt-get update && apt-get upgrade -y

RUN apt-get install -y --no-install-recommends \
    libreoffice \
    fonts-dejavu \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY assets/ ./assets/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]