FROM python:3.13-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System dependencies (GDAL for PostGIS/GIS support)
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash build-essential gcc g++ \
    gdal-bin libgdal-dev \
    postgresql-client \
    netcat-openbsd \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip

RUN mkdir -p /app/media /app/logs /app/staticfiles

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY entrypoint.sh ./
COPY . .

RUN chmod +x entrypoint.sh && \
    chmod -R 755 /app/media /app/staticfiles

EXPOSE 8000
ENTRYPOINT ["/bin/bash", "/app/entrypoint.sh"]
