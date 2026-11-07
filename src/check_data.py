import sys
import pandas as pd
import hashlib
from pathlib import Path

EXPECTED_COLUMNS = [
    'dur', 'proto', 'service', 'state', 'spkts', 'dpkts', 'sbytes', 'dbytes',
    'rate', 'sload', 'dload', 'sloss', 'dloss', 'sinpkt', 'dinpkt', 'sjit',
    'djit', 'swin', 'stcpb', 'dtcpb', 'dwin', 'tcprtt', 'synack', 'ackdat',
    'smean', 'dmean', 'trans_depth', 'response_body_len', 'ct_src_dport_ltm',
    'ct_dst_sport_ltm', 'is_ftp_login', 'ct_ftp_cmd', 'ct_flw_http_mthd',
    'is_sm_ips_ports', 'label'
]

# Хэш уже вшит!
EXPECTED_HASH = "9463584bea45b55962d50865fd1abd16332b573105103f11f1e0bd978e6c9c7f"

def check_data(filepath: str):
    path = Path(filepath)
    if not path.exists():
        print(f"ERROR: Файл {filepath} не найден.")
        sys.exit(1)

    with open(path, 'rb') as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
    if file_hash != EXPECTED_HASH:
        print(f"ERROR: Хэш не совпадает! Ожидался: {EXPECTED_HASH}, получен: {file_hash}")
        sys.exit(1)
    print("✓ Целостность данных подтверждена (SHA256).")

    df = pd.read_csv(path)
    missing_cols = set(EXPECTED_COLUMNS) - set(df.columns)
    if missing_cols:
        print(f"ERROR: Отсутствуют колонки: {missing_cols}")
        sys.exit(1)
    print("✓ Схема данных корректна.")

    if df.isna().any().any():
        print("ERROR: Обнаружены пропущенные значения (NaN).")
        sys.exit(1)
    print("✓ Пропуски (NaN) отсутствуют.")

    if len(df) < 50:
        print(f"ERROR: Датасет слишком мал ({len(df)} строк). Минимум: 50.")
        sys.exit(1)
    print(f"✓ Объём данных достаточен ({len(df)} строк).")

    print("\n[DATA GATE PASSED] Все проверки данных пройдены успешно.")

if __name__ == "__main__":
    target_file = sys.argv[1] if len(sys.argv) > 1 else "data/ci_sample.csv"
    check_data(target_file)
