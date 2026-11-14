# ==============================================================================
# Dockerfile for Agent Orchestrator Microservice (Port 8003)
# ==============================================================================
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY shared /app/shared
COPY services/__init__.py /app/services/__init__.py
COPY services/profile_memory_service /app/services/profile_memory_service
COPY services/rag_retrieval_service /app/services/rag_retrieval_service
COPY services/agent_orchestrator_service /app/services/agent_orchestrator_service

ENV PYTHONPATH=/app
EXPOSE 8003

CMD ["uvicorn", "services.agent_orchestrator_service.main:app", "--host", "0.0.0.0", "--port", "8003"]

