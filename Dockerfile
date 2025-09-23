# ---- Base (Debian 12 / bookworm) ----
FROM python:3.12-slim

# Keep Python logs unbuffered and avoid .pyc files
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    TZ=Europe/Paris

# Minimal runtime deps:
# - tzdata: timezone handling for logs
# - ca-certificates: TLS
# - libffi8: runtime for cffi
# - libsodium23: (usually not needed w/ PyNaCl wheels, but harmless/safe)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata \
    ca-certificates \
    libffi8 \
    libsodium23 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 10001 thanksbotuser
WORKDIR /app

# Install Python deps first for better layer caching
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# Copy the bot code
COPY . /app

# Drop privileges for runtime
USER thanksbotuser

# If your entrypoint is main.py at project root:
CMD ["python", "main.py"]
