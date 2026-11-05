import pandas as pd
import numpy as np
import joblib
from pathlib import Path

# Загружаем модель при импорте модуля
MODEL_PATH = Path(__file__).parent.parent / "models" / "baseline_pipeline.joblib"
pipeline = joblib.load(MODEL_PATH)

# Ожидаемые колонки (без target и attack_cat)
EXPECTED_COLUMNS = [
    'dur', 'proto', 'service', 'state', 'spkts', 'dpkts', 'sbytes', 'dbytes',
    'rate', 'sload', 'dload', 'sloss', 'dloss', 'sinpkt', 'dinpkt', 'sjit',
    'djit', 'swin', 'stcpb', 'dtcpb', 'dwin', 'tcprtt', 'synack', 'ackdat',
    'smean', 'dmean', 'trans_depth', 'response_body_len', 'ct_src_dport_ltm',
    'ct_dst_sport_ltm', 'is_ftp_login', 'ct_ftp_cmd', 'ct_flw_http_mthd',
    'is_sm_ips_ports'
]

MAX_ROWS = 1000  # Лимит на количество записей за один запрос

def predict_traffic(input_data) -> np.ndarray:
    """
    Единая функция предсказания с валидацией входов.
    
    Args:
        input_data: pandas DataFrame с признаками сетевого трафика.
        
    Returns:
        np.ndarray: Предсказанные метки (0 или 1).
        
    Raises:
        TypeError: Если вход не является pandas DataFrame.
        ValueError: Если нарушены ограничения на размер, колонки или значения.
    """
    # 1. Проверка типа данных
    if not isinstance(input_data, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(input_data).__name__}")
    
    # 2. Проверка на пустой вход
    if input_data.empty:
        raise ValueError("Input DataFrame is empty")
    
    # 3. Проверка лимита размера (защита от DoS по памяти)
    if len(input_data) > MAX_ROWS:
        raise ValueError(f"Input exceeds maximum allowed rows ({MAX_ROWS}). Got {len(input_data)}")
    
    # 4. Проверка наличия всех ожидаемых колонок
    missing_cols = set(EXPECTED_COLUMNS) - set(input_data.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # 5. Проверка на NaN и Inf
    if input_data.isna().any().any():
        raise ValueError("Input data contains NaN values")
    if np.isinf(input_data.select_dtypes(include=[np.number]).values).any():
        raise ValueError("Input data contains Inf values")
    
    # 6. Если всё ок, делаем предсказание
    # Берем только ожидаемые колонки в правильном порядке
    X_valid = input_data[EXPECTED_COLUMNS]
    predictions = pipeline.predict(X_valid)
    
    return predictions