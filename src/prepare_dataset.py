from pathlib import Path
import urllib.request

import pandas as pd
from sklearn.model_selection import StratifiedShuffleSplit

REPO = "ju4700/APEX-IDS2026"
FILE_PATH = "Machine%20Learnign/data/UNSW_NB15_testing-set.parquet"
BRANCHES = ["main", "master"]

ROOT = Path(__file__).resolve().parents[1]
TMP_DIR = ROOT / "tmp"
SRC_FILE = TMP_DIR / "UNSW_NB15_testing-set.parquet"
OUT_FILE = ROOT / "data" / "dataset.csv"

SAMPLE_SIZE = 15000
RANDOM_STATE = 42


def download_source() -> Path:
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    last_error = None

    for branch in BRANCHES:
        url = f"https://raw.githubusercontent.com/{REPO}/{branch}/{FILE_PATH}"
        print(f"Trying branch: {branch}")
        print(f"URL: {url}")

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "python"})
            with urllib.request.urlopen(req, timeout=60) as resp:  # nosec B310
                data = resp.read()

            SRC_FILE.write_bytes(data)
            print(f"Downloaded: {SRC_FILE}")
            return SRC_FILE

        except Exception as exc:
            last_error = exc
            print(f"Failed for branch {branch}: {exc}")

    raise RuntimeError(f"All download attempts failed. Last error: {last_error}")


def prepare_sample(source_path: Path) -> None:
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_parquet(source_path)

    print(f"Source rows: {len(df)}")
    print(f"Source columns: {df.shape[1]}")
    print("Source label counts:")
    print(df["label"].value_counts())

    sss = StratifiedShuffleSplit(
        n_splits=1,
        train_size=SAMPLE_SIZE,
        random_state=RANDOM_STATE,
    )

    train_idx, _ = next(sss.split(df, df["label"]))
    sample = df.iloc[train_idx].reset_index(drop=True)

    sample.to_csv(OUT_FILE, index=False)

    print(f"Saved rows: {len(sample)}")
    print(f"Saved columns: {sample.shape[1]}")
    print(f"Output file: {OUT_FILE}")
    print("Sample label counts:")
    print(sample["label"].value_counts())
    print("Sample attack_cat counts:")
    print(sample["attack_cat"].value_counts())


def main() -> None:
    source_path = download_source()
    prepare_sample(source_path)


if __name__ == "__main__":
    main()
