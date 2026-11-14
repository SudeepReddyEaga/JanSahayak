# ==============================================================================
# Dockerfile for API Gateway Microservice (Port 8000)
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
COPY services/voice_speech_service /app/services/voice_speech_service
COPY services/api_gateway /app/services/api_gateway
COPY services/frontend_ui/static /app/services/frontend_ui/static

ENV PYTHONPATH=/app
EXPOSE 8000

CMD ["uvicorn", "services.api_gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]

