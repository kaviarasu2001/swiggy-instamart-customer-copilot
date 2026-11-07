
import joblib
import pandas as pd
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = PROJECT_DIR / "models" / "churn_model_improved.pkl"

model = joblib.load(MODEL_PATH)


def predict_churn(frequency, monetary):

    customer = pd.DataFrame({
        "Frequency": [frequency],
        "Monetary": [monetary]
    })

    prediction = model.predict(customer)[0]
    probabilities = model.predict_proba(customer)[0]

    return {
        "prediction": int(prediction),
        "churn_probability": round(probabilities[1] * 100, 2),
        "non_churn_probability": round(probabilities[0] * 100, 2)
    }


if __name__ == "__main__":

    print("SWIGGY INSTAMART CHURN PREDICTION")
    print("=" * 45)

    frequency = float(input("Enter delivered orders: "))
    monetary = float(input("Enter total spending (Rs): "))

    result = predict_churn(frequency, monetary)

    print("\nPREDICTION RESULT")
    print("=" * 30)

    if result["prediction"] == 1:
        print("Customer is potentially at risk of churn.")
    else:
        print("Customer is not flagged as churned.")

    print("Churn probability:", result["churn_probability"], "%")
    print("Non-churn probability:", result["non_churn_probability"], "%")
