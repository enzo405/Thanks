# ---- Base (Debian 12 / bookworm) ----
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    TZ=Europe/Paris

RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata \
    ca-certificates \
    libffi8 \
    libsodium23 \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 10001 thanksbotuser
WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY . /app

USER thanksbotuser

CMD ["python", "main.py"]