# Lab 1: Secure ML Environment

## 1. Project Direction
- **Direction:** Structured Data (Network Intrusion Detection)
- **Dataset:** UNSW-NB15 (15,000 rows stratified sample)
- **Source:** https://github.com/ju4700/APEX-IDS2026

## 2. Security Checks
- **SSH:** Root login disabled (`PermitRootLogin no`), Ed25519 keys used.
- **Firewall:** UFW enabled, default deny incoming, `limit 22/tcp`.
- **Dependencies:** `pip-audit` passed (No known vulnerabilities found).
- **Dataset Integrity (SHA256):** `5a9ca6fa1d14d68d17f35fc4a942c68d061f90bb26bf43c1f308ff9bdc9698f6`

## 3. Mini Threat Model
| Asset | Threat | Countermeasure | Status |
|---|---|---|---|
| SSH Server | Brute-force / Root access | SSH keys, `PermitRootLogin no`, UFW limit | Implemented |
| Dataset | Data poisoning / Substitution | SHA256 integrity check, `.gitignore` | Implemented |
| Git Repo | Secret leakage | `.gitignore` for `.env`, `data/`, `models/` | Implemented |
| Dependencies | Supply chain vulnerabilities | `pip-audit`, pinned `requirements.txt` | Implemented |
