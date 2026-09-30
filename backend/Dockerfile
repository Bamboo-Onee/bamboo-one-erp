# ==============================================================================
# BACKEND DOCKERFILE - FASTAPI COM PYTHON 3.12 (CLEAN ARCHITECTURE)
# ==============================================================================
FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

WORKDIR /app

# Instalação de dependências de sistema necessárias para compilação e libs C
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalação de dependências do Python
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Cópia do código-fonte e testes
COPY . /app/

EXPOSE 8000

# Execução assíncrona com Uvicorn apontando para src/main.py
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
