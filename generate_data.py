
import os
import numpy as np
import pandas as pd

# Reproducible random data
np.random.seed(42)

# Project data folder
BASE_PATH = "/content/instamart-copilot-workspace"
DATA_PATH = os.path.join(BASE_PATH, "data")
os.makedirs(DATA_PATH, exist_ok=True)

# Dataset sizes
NUM_CUSTOMERS = 1000
NUM_ORDERS = 5000
NUM_TICKETS = 1000

# -----------------------------------
# 1. GENERATE CUSTOMER DATA
# -----------------------------------

cities = ["Coimbatore", "Chennai", "Bangalore", "Hyderabad",
          "Mumbai", "Pune", "Delhi"]

genders = ["Male", "Female", "Other"]

customers = pd.DataFrame({
    "customer_id": [f"CUST{i:04d}" for i in range(1, NUM_CUSTOMERS + 1)],
    "city": np.random.choice(cities, NUM_CUSTOMERS),
    "gender": np.random.choice(genders, NUM_CUSTOMERS),
    "age": np.random.randint(18, 65, NUM_CUSTOMERS),
    "signup_date": pd.to_datetime(
        np.random.choice(
            pd.date_range("2023-01-01", "2026-10-31"),
            NUM_CUSTOMERS
        )
    )
})

# -----------------------------------
# 2. GENERATE ORDER DATA
# -----------------------------------

order_statuses = ["Delivered", "Cancelled", "Returned"]
payment_methods = ["UPI", "Card", "Cash", "Wallet"]

orders = pd.DataFrame({
    "order_id": [f"ORD{i:05d}" for i in range(1, NUM_ORDERS + 1)],
    "customer_id": np.random.choice(
        customers["customer_id"], NUM_ORDERS
    ),
    "order_date": pd.to_datetime(
        np.random.choice(
            pd.date_range("2025-01-01", "2026-10-31"),
            NUM_ORDERS
        )
    ),
    "order_amount": np.round(
        np.random.uniform(100, 3000, NUM_ORDERS), 2
    ),
    "order_status": np.random.choice(
        order_statuses, NUM_ORDERS, p=[0.88, 0.08, 0.04]
    ),
    "payment_method": np.random.choice(
        payment_methods, NUM_ORDERS
    )
})

# -----------------------------------
# 3. GENERATE SUPPORT TICKETS
# -----------------------------------

issue_categories = [
    "Delivery Delay",
    "Payment Issue",
    "Product Quality",
    "Missing Item",
    "Refund Request"
]

ticket_descriptions = {
    "Delivery Delay": "My order has not arrived on time.",
    "Payment Issue": "My payment was deducted but order confirmation failed.",
    "Product Quality": "The product received was damaged or poor quality.",
    "Missing Item": "One or more items are missing from my order.",
    "Refund Request": "I want a refund for my order."
}

ticket_categories = np.random.choice(
    issue_categories, NUM_TICKETS
)

tickets = pd.DataFrame({
    "ticket_id": [f"TKT{i:05d}" for i in range(1, NUM_TICKETS + 1)],
    "customer_id": np.random.choice(
        customers["customer_id"], NUM_TICKETS
    ),
    "order_id": np.random.choice(
        orders["order_id"], NUM_TICKETS
    ),
    "issue_category": ticket_categories,
    "description": [
        ticket_descriptions[category]
        for category in ticket_categories
    ],
    "priority": np.random.choice(
        ["Low", "Medium", "High"], NUM_TICKETS
    ),
    "ticket_status": np.random.choice(
        ["Open", "In Progress", "Resolved"], NUM_TICKETS
    ),
    "created_at": pd.to_datetime(
        np.random.choice(
            pd.date_range("2025-01-01", "2026-10-31"),
            NUM_TICKETS
        )
    )
})

# -----------------------------------
# 4. GENERATE POLICY EVALUATION DATA
# -----------------------------------

policy_records = [
    {
        "query": "My order is delayed. What should I do?",
        "policy_category": "Delivery",
        "expected_action": "Check delivery status and escalate if necessary."
    },
    {
        "query": "I was charged twice for one order.",
        "policy_category": "Payment",
        "expected_action": "Verify payment transactions and investigate duplicate charges."
    },
    {
        "query": "I received a damaged product.",
        "policy_category": "Product Quality",
        "expected_action": "Collect evidence and review refund or replacement eligibility."
    },
    {
        "query": "I want to cancel my order.",
        "policy_category": "Cancellation",
        "expected_action": "Check order status and applicable cancellation conditions."
    },
    {
        "query": "When will I receive my refund?",
        "policy_category": "Refund",
        "expected_action": "Verify refund approval and explain the applicable timeline."
    }
]

policy_evaluation = pd.DataFrame(policy_records)

# -----------------------------------
# 5. SAVE ALL DATASETS
# -----------------------------------

datasets = {
    "customers.csv": customers,
    "orders.csv": orders,
    "tickets.csv": tickets,
    "policy_evaluation.csv": policy_evaluation
}

for filename, dataframe in datasets.items():
    file_path = os.path.join(DATA_PATH, filename)
    dataframe.to_csv(file_path, index=False)
    print(f"Created: {filename} | Rows: {len(dataframe)}")

print("\nAll synthetic datasets generated successfully!")
