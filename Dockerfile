# ==============================================================================
# Portable All-in-One Docker Image for Universal Single-Command Execution
# Bundles Redis + all 5 FastAPI microservices + Interactive Web UI inside one image:
#   docker build -t multilingual-scheme-guide .
#   docker run -p 8000:8000 multilingual-scheme-guide
# (For multi-container PostgreSQL + Nginx deployment, use: docker compose up --build)
# ==============================================================================
FROM python:3.12-slim

WORKDIR /app

# Install redis-server so Redis caching works inside the standalone portable image
RUN apt-get update \
    && apt-get install -y --no-install-recommends redis-server \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (Microsoft Agent Framework, FastAPI, SQLAlchemy, Redis, etc.)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy entire application codebase
COPY shared /app/shared
COPY services /app/services
COPY docker/entrypoint.allinone.sh /app/entrypoint.allinone.sh

# Normalize line endings and mark entrypoint executable
RUN sed -i 's/\r$//' /app/entrypoint.allinone.sh && chmod +x /app/entrypoint.allinone.sh

# Persist SQLite DB volume under /app/data when PostgreSQL is externalized
RUN mkdir -p /app/data

ENV PYTHONPATH=/app \
    ORCHESTRATION_MODE=microservice_http \
    DATABASE_URL=sqlite:////app/data/scheme_guide.db \
    REDIS_URL=redis://127.0.0.1:6379/0 \
    PROFILE_MEMORY_SERVICE_URL=http://127.0.0.1:8001 \
    RAG_RETRIEVAL_SERVICE_URL=http://127.0.0.1:8002 \
    AGENT_ORCHESTRATOR_SERVICE_URL=http://127.0.0.1:8003 \
    VOICE_SPEECH_SERVICE_URL=http://127.0.0.1:8004 \
    LLM_PROVIDER=deterministic

EXPOSE 8000

CMD ["/app/entrypoint.allinone.sh"]

