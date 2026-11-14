# ==============================================================================
# Dockerfile for Profile Memory Microservice (Port 8001)
# ==============================================================================
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies cleanly without caching wheel bloat
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy shared domain/infrastructure layer and this microservice module
COPY shared /app/shared
COPY services/__init__.py /app/services/__init__.py
COPY services/profile_memory_service /app/services/profile_memory_service

ENV PYTHONPATH=/app
EXPOSE 8001

CMD ["uvicorn", "services.profile_memory_service.main:app", "--host", "0.0.0.0", "--port", "8001"]

