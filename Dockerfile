# Dockerfile for AI Website Cloner
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    fastapi==0.109.0 \
    uvicorn[standard]==0.27.0 \
    python-multipart==0.0.6 \
    pydantic==2.5.3 \
    beautifulsoup4==4.12.3 \
    aiohttp==3.9.1

RUN pip install --no-cache-dir playwright && \
    playwright install chromium --with-deps

COPY . .

RUN mkdir -p /app/database /app/cloned_sites /app/assets/images /app/projects

ENV PYTHONUNBUFFERED=1
ENV PORT=10000

EXPOSE 10000

CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "10000"]
