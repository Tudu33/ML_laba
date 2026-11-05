import pytest
import pandas as pd
import numpy as np
from src.predict import predict_traffic, EXPECTED_COLUMNS, MAX_ROWS

# --- Fixture: валидные данные для тестов ---
@pytest.fixture
def valid_sample():
    # Создаем одну валидную строку с нулевыми/дефолтными значениями
    data = {col: 0.0 if col not in ['proto', 'service', 'state'] else 'unknown' for col in EXPECTED_COLUMNS}
    return pd.DataFrame([data])

# --- Тест 1: Позитивный (корректный вход) ---
def test_predict_valid_input(valid_sample):
    predictions = predict_traffic(valid_sample)
    assert isinstance(predictions, np.ndarray)
    assert len(predictions) == 1
    assert predictions[0] in [0, 1]

# --- Тест 2: Негативный (неверный тип данных) ---
def test_predict_invalid_type():
    with pytest.raises(TypeError, match="Expected pandas DataFrame"):
        predict_traffic("this is a string, not a dataframe")

# --- Тест 3: Негативный (отсутствуют обязательные колонки) ---
def test_predict_missing_columns(valid_sample):
    bad_df = valid_sample.drop(columns=['dur', 'rate'])
    with pytest.raises(ValueError, match="Missing required columns"):
        predict_traffic(bad_df)

# --- Тест 4: Негативный (наличие NaN значений) ---
def test_predict_nan_values(valid_sample):
    bad_df = valid_sample.copy()
    bad_df.loc[0, 'sbytes'] = np.nan
    with pytest.raises(ValueError, match="contains NaN values"):
        predict_traffic(bad_df)

# --- Тест 5: Негативный (превышение лимита строк) ---
def test_predict_exceeds_max_rows(valid_sample):
    # Создаем датафрейм, превышающий лимит MAX_ROWS
    large_df = pd.concat([valid_sample] * (MAX_ROWS + 10), ignore_index=True)
    with pytest.raises(ValueError, match=rf"exceeds maximum allowed rows \({MAX_ROWS}\)"):
        predict_traffic(large_df)