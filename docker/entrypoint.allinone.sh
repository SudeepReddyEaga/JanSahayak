#!/usr/bin/env bash
# ==============================================================================
# Standalone All-in-One Entrypoint Script
# Starts Redis + all 5 microservices inside one portable Docker container.
# ==============================================================================
set -e

# 1. Start Redis daemon in background
redis-server --daemonize yes --dir /app/data --appendonly yes

# 2. Start Profile Memory Microservice (Port 8001) and wait until ready
uvicorn services.profile_memory_service.main:app --host 127.0.0.1 --port 8001 &
python -c "import time, urllib.request
for _ in range(30):
    try:
        urllib.request.urlopen('http://127.0.0.1:8001/health', timeout=1)
        break
    except Exception:
        time.sleep(0.5)"

# 3. Start RAG Retrieval Microservice (Port 8002) and wait until ready
uvicorn services.rag_retrieval_service.main:app --host 127.0.0.1 --port 8002 &
python -c "import time, urllib.request
for _ in range(30):
    try:
        urllib.request.urlopen('http://127.0.0.1:8002/health', timeout=1)
        break
    except Exception:
        time.sleep(0.5)"

# 4. Start Agent Orchestrator Microservice (Port 8003) and wait until ready
uvicorn services.agent_orchestrator_service.main:app --host 127.0.0.1 --port 8003 &
python -c "import time, urllib.request
for _ in range(30):
    try:
        urllib.request.urlopen('http://127.0.0.1:8003/health', timeout=1)
        break
    except Exception:
        time.sleep(0.5)"

# 5. Start Voice & Speech Microservice (Port 8004) and wait until ready
uvicorn services.voice_speech_service.main:app --host 127.0.0.1 --port 8004 &
python -c "import time, urllib.request
for _ in range(30):
    try:
        urllib.request.urlopen('http://127.0.0.1:8004/health', timeout=1)
        break
    except Exception:
        time.sleep(0.5)"

# 6. Run public API Gateway + Interactive Web UI in foreground on Port 8000
exec uvicorn services.api_gateway.main:app --host 0.0.0.0 --port 8000

