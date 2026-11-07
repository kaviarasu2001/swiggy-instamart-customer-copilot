
import joblib
import pandas as pd
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = PROJECT_DIR / "models" / "ticket_classifier.pkl"

ticket_model = joblib.load(MODEL_PATH)

TEAM_ROUTING = {
    "Delivery Delay": "Delivery Support",
    "Refund Request": "Refund Team",
    "Missing Item": "Order Support",
    "Payment Issue": "Payment Support",
    "Product Quality": "Quality Support"
}


def classify_ticket(description):
    category = ticket_model.predict([description])[0]

    team = TEAM_ROUTING.get(
        category,
        "General Support"
    )

    return {
        "category": category,
        "team": team
    }


def process_ticket(description, priority="Medium", status="Open"):

    result = classify_ticket(description)

    return {
        "description": description,
        "category": result["category"],
        "priority": priority,
        "team": result["team"],
        "status": status
    }


if __name__ == "__main__":

    complaint = input("Enter customer complaint: ")

    result = process_ticket(complaint)

    print("\nCUSTOMER SUPPORT TICKET")
    print("=" * 40)

    for key, value in result.items():
        print(f"{key.title()}: {value}")
