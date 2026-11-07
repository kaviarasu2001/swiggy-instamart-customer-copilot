
import pandas as pd
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"

def clean_customers():
    df = pd.read_csv(DATA_DIR / "customers.csv")
    df = df.drop_duplicates()
    df["city"] = df["city"].astype(str).str.strip().str.title()
    df["gender"] = df["gender"].astype(str).str.strip().str.title()
    df["age"] = pd.to_numeric(df["age"], errors="coerce")
    df.loc[(df["age"] < 13) | (df["age"] > 100), "age"] = None
    df["age"] = df["age"].fillna(df["age"].median())
    df.to_csv(DATA_DIR / "cleaned" / "customers_cleaned.csv", index=False)
    return df

def clean_orders():
    df = pd.read_csv(DATA_DIR / "orders.csv")
    df = df.drop_duplicates()
    df["order_amount"] = pd.to_numeric(df["order_amount"], errors="coerce")
    df.loc[df["order_amount"] < 0, "order_amount"] = None
    df["order_amount"] = df["order_amount"].fillna(df["order_amount"].median())
    df["payment_method"] = df["payment_method"].astype(str).str.strip().str.title()
    df["order_status"] = df["order_status"].astype(str).str.strip().str.title()
    df.to_csv(DATA_DIR / "cleaned" / "orders_cleaned.csv", index=False)
    return df

def clean_tickets():
    df = pd.read_csv(DATA_DIR / "tickets.csv")
    df = df.drop_duplicates()
    df["description"] = df["description"].fillna("No description provided")
    df["issue_category"] = df["issue_category"].astype(str).str.strip().str.title()
    df["priority"] = df["priority"].astype(str).str.strip().str.title()
    df["ticket_status"] = df["ticket_status"].astype(str).str.strip().str.title()
    df.to_csv(DATA_DIR / "cleaned" / "tickets_cleaned.csv", index=False)
    return df

if __name__ == "__main__":
    print("Cleaning customers...")
    print("Customers:", len(clean_customers()))

    print("Cleaning orders...")
    print("Orders:", len(clean_orders()))

    print("Cleaning tickets...")
    print("Tickets:", len(clean_tickets()))

    print("\nData cleaning completed!")
