# ML Security Labs 1 & 2: Secure Environment & Baseline Model

## 1. Project Overview
- **Direction:** Structured Data (Network Intrusion Detection)
- **Dataset:** UNSW-NB15 (10,719 unique rows after deduplication)
- **Baseline Model:** Logistic Regression (with StandardScaler + OneHotEncoder)
- **Main Metrics:** Accuracy = 0.7794, F1-macro = 0.7767 (Test size: 2144)

## 2. Security & Integrity Checks
- **SSH:** Root login disabled (`PermitRootLogin no`), Ed25519 keys only.
- **Firewall:** UFW enabled, default deny incoming, `limit 22/tcp`.
- **Network Surface:** Minimized (only `sshd` and local `containerd` listening).
- **Dataset Integrity (SHA256):** `5a9ca6fa1d14d68d17f35fc4a942c68d061f90bb26bf43c1f308ff9bdc9698f6`
- **Model Integrity (SHA256):** `2877a05b7d902249780b0c1df36760d29aa3d95ff57be962c01b7018c1128bd3`
- **Dependency Audit:** `pip-audit` (No known vulnerabilities), `bandit` (No issues identified).

## 3. How to Run & Verify

    # 1. Activate environment
    source .venv/bin/activate

    # 2. Run automated tests (1 positive, 4 negative)
    python -m pytest tests/test_predict.py -v

    # 3. Run static security analysis
    bandit -r src/

    # 4. Secure Jupyter access (run on VM)
    jupyter lab --ip=127.0.0.1 --no-browser
    # Connect from host machine via SSH tunnel:
    # ssh -L 8888:127.0.0.1:8888 mluser@192.168.3.82

## 4. Mini Threat Model

| Asset | Threat | Countermeasure | Status |
|---|---|---|---|
| Input API (`predict_traffic`) | Malformed/oversized payload (DoS) | Strict type/shape validation, `MAX_ROWS=1000` limit | Implemented |
| Model Artifact | Model substitution / Tampering | SHA256 integrity check, `.gitignore` | Implemented |
| Jupyter Environment | Unauthorized network access | Bound to `127.0.0.1`, password protected, SSH tunnel only | Implemented |
| Python Dependencies | Supply chain vulnerabilities | `pip-audit`, `bandit`, pinned `requirements.txt` | Implemented |