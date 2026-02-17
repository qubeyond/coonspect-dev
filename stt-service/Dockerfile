FROM nvidia/cuda:12.4.1-runtime-ubuntu22.04

# ffmpeg - для обработки звука
# python3.11 - основа
# curl - для установки uv
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 \
    python3-pip \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project

COPY . .

RUN uv sync --frozen

ENV PATH="/app/.venv/bin:$PATH"

ENV HF_HOME=/app/cache/huggingface

CMD ["python", "-m", "app.main"]
# CMD ["taskiq", "worker", "app.worker:redis_broker"]