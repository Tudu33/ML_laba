FROM python:3.11.9-slim-bookworm

# 1. Обновляем системные пакеты для закрытия уязвимостей
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

# 2. Создаем пользователя без прав root (UID 1000)
RUN useradd -m -u 1000 mluser

# 3. Устанавливаем зависимости
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Копируем код, модель, данные и тесты
COPY src/ /app/src/
COPY models/ /app/models/
COPY data/ci_sample.csv /app/data/ci_sample.csv
COPY static/ /app/static/
COPY app.py /app/app.py
COPY tests/ /app/tests/

# 5. Переключаемся на non-root пользователя
USER mluser

# 6. Открываем порт для FastAPI
EXPOSE 8001

# 7. Проверка здоровья контейнера (используем встроенный python, т.к. curl может отсутствовать в slim)
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8001/health')" || exit 1

# 8. Запускаем приложение
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]
