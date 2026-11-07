FROM python:3.11.9-slim-bookworm

# Переменные окружения для корректной работы Python в контейнере
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*
ENV PYTHONPATH=/app

# Создаем непривилегированного пользователя (НЕ root!)
RUN useradd -m -u 1000 mluser

# Копируем и устанавливаем ТОЛЬКО runtime-зависимости
COPY requirements-runtime.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements-runtime.txt

# Копируем только необходимые файлы приложения
COPY src/ ./src/
COPY models/baseline_pipeline.joblib ./models/baseline_pipeline.joblib
COPY data/ci_sample.csv ./data/ci_sample.csv

# Меняем владельца файлов на нашего пользователя
RUN chown -R mluser:mluser /app

# Переключаемся на непривилегированного пользователя
USER mluser

# Smoke-проверка: команда по умолчанию пытается сделать предсказание
CMD ["python", "src/smoke_test.py"]
