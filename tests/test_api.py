"""
Автоматические тесты API для ЛР4.
Проверяют корректность обработки ошибок и ограничений.
"""
import pytest
import pandas as pd
import sys
import os

# Добавляем корень проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from fastapi.testclient import TestClient

# Правильный токен для тестов
VALID_TOKEN = "demo-secret-token-123"

# Фикстура для правильного запуска lifespan (загрузки модели)
@pytest.fixture(scope="module")
def client():
    """Создаёт TestClient с правильно загруженной моделью."""
    with TestClient(app) as c:
        yield c


class TestHealthEndpoint:
    """Тесты эндпоинта /health"""
    
    def test_health_success(self, client):
        """Тест 1: /health возвращает 200, когда модель загружена"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["model_version"] == "lab2-v1"


class TestPredictEndpoint:
    """Тесты эндпоинта /predict"""
    
    def test_predict_missing_token(self, client):
        """Тест 2: Запрос без токена возвращает 401"""
        payload = {"dur": 0.0, "proto": "tcp"}
        response = client.post("/predict", json=payload)
        assert response.status_code == 401
        assert "Invalid or missing API token" in response.json()["detail"]
    
    def test_predict_invalid_token(self, client):
        """Тест 3: Неверный токен возвращает 401"""
        payload = {"dur": 0.0, "proto": "tcp"}
        response = client.post(
            "/predict",
            json=payload,
            headers={"X-API-Token": "wrong-token"}
        )
        assert response.status_code == 401
        assert "Invalid or missing API token" in response.json()["detail"]
    
    def test_predict_empty_payload(self, client):
        """Тест 4: Пустой JSON возвращает 400"""
        response = client.post(
            "/predict",
            json={},
            headers={"X-API-Token": VALID_TOKEN}
        )
        assert response.status_code == 400
    
    def test_predict_missing_columns(self, client):
        """Тест 5: Отсутствие обязательных колонок возвращает 400"""
        payload = {"dur": 0.0, "proto": "tcp"}  # Не хватает 32 колонок
        response = client.post(
            "/predict",
            json=payload,
            headers={"X-API-Token": VALID_TOKEN}
        )
        assert response.status_code == 400
        assert "Missing required columns" in response.json()["detail"]
    
    def test_predict_nan_values(self, client):
        """Тест 6: NaN (null в JSON) в данных возвращает 400"""
        # Читаем реальные данные из файла и делаем одну строку
        df = pd.read_csv('data/ci_sample.csv').head(1)
        payload = df.to_dict(orient='records')[0]
        
        # Заменяем значение на None. В JSON это станет null, а pandas прочитает как NaN
        payload['sbytes'] = None
        
        response = client.post(
            "/predict",
            json=payload,
            headers={"X-API-Token": VALID_TOKEN}
        )
        assert response.status_code == 400
        assert "NaN" in response.json()["detail"]


class TestRateLimiting:
    """Тесты ограничения частоты запросов"""
    
    def test_rate_limit_exceeded(self, client):
        """Тест 7: Превышение rate limit возвращает 429"""
        # Отправляем 15 запросов подряд (лимит 10/минуту)
        payload = {"dur": 0.0, "proto": "tcp", "service": "http", "state": "FIN"}
        
        responses = []
        for _ in range(15):
            response = client.post(
                "/predict",
                json=payload,
                headers={"X-API-Token": VALID_TOKEN}
            )
            responses.append(response.status_code)
        
        # Хотя бы один запрос должен быть отклонён с 429
        assert 429 in responses


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
