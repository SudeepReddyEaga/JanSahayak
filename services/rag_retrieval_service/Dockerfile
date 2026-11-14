# ==============================================================================
# Dockerfile for RAG Retrieval Microservice (Port 8002)
# ==============================================================================
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY shared /app/shared
COPY services/__init__.py /app/services/__init__.py
COPY services/rag_retrieval_service /app/services/rag_retrieval_service

ENV PYTHONPATH=/app
EXPOSE 8002

CMD ["uvicorn", "services.rag_retrieval_service.main:app", "--host", "0.0.0.0", "--port", "8002"]

