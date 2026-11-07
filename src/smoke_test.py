import pandas as pd
from src.predict import predict_traffic

def main() -> None:
    df = pd.read_csv("data/ci_sample.csv")
    sample = df.drop(columns=["label", "attack_cat"]).head(1)
    prediction = predict_traffic(sample)
    print("Smoke test passed")
    print(f"Input shape: {sample.shape}")
    print(f"Prediction: {prediction}")

if __name__ == "__main__":
    main()
