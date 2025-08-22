FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app
ENV PIP_DEFAULT_TIMEOUT=120

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
# Retry loop to mitigate transient PyPI timeouts
RUN /bin/sh -c 'i=0; \
    until [ $i -ge 5 ]; do \
      pip install --no-cache-dir --timeout 120 -r requirements.txt && break; \
      i=$((i+1)); echo "pip failed, retrying in 5s ($i)"; sleep 5; \
    done; \
    [ $i -lt 5 ]'

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
