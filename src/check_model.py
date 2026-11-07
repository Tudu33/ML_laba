import sys
import json
from pathlib import Path

def check_model(baseline_path: str, candidate_path: str):
    try:
        with open(baseline_path, 'r') as f:
            baseline = json.load(f)
        with open(candidate_path, 'r') as f:
            candidate = json.load(f)
    except Exception as e:
        print(f"ERROR: Не удалось загрузить метрики. {e}")
        sys.exit(1)

    baseline_f1 = baseline.get('f1_macro')
    candidate_f1 = candidate.get('f1_macro')

    if baseline_f1 is None or candidate_f1 is None:
        print("ERROR: Метрика 'f1_macro' отсутствует в одном из файлов.")
        sys.exit(1)

    threshold = baseline_f1 * 0.95
    
    print(f"Baseline F1-macro: {baseline_f1:.4f}")
    print(f"Candidate F1-macro: {candidate_f1:.4f}")
    print(f"Допустимый порог (95% от baseline): {threshold:.4f}")

    if candidate_f1 >= threshold:
        print("\n[MODEL GATE PASSED] Качество модели приемлемо.")
        sys.exit(0)
    else:
        print(f"\n[MODEL GATE FAILED] Ухудшение качества недопустимо! ({candidate_f1:.4f} < {threshold:.4f})")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Использование: python check_model.py <baseline.json> <candidate.json>")
        sys.exit(1)
    check_model(sys.argv[1], sys.argv[2])
