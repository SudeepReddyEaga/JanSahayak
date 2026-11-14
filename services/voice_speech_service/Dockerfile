FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared/ ./shared/
COPY services/__init__.py ./services/__init__.py
COPY services/voice_speech_service/ ./services/voice_speech_service/

EXPOSE 8004
CMD ["uvicorn", "services.voice_speech_service.main:app", "--host", "0.0.0.0", "--port", "8004"]

