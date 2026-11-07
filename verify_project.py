from pathlib import Path
import json
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parent
checks = []

def check(name, condition, detail=""):
    status = bool(condition)
    checks.append(status)
    print(
        f"{'PASSED' if status else 'FAILED'}: {name}"
        + (f" | {detail}" if detail else "")
    )

print("=" * 65)
print("SWIGGY INSTAMART CAPSTONE - FINAL VERIFICATION")
print("=" * 65)

required_files = [
    "generate_data.py",
    "mock_llm.py",
    "requirements.txt",
    "README.md",
    "data/clean/customers.csv",
    "data/clean/products.csv",
    "data/clean/orders.csv",
    "data/clean/tickets_redacted.csv",
    "data/instamart.db",
    "data/raw/policy_eval.csv",
    "data/raw/agent_scenarios.csv",
    "sql/queries.sql",
    "outputs/customer_segments.csv",
    "outputs/lapse_model.joblib",
    "outputs/retention_list.csv",
    "outputs/triage_results.csv",
    "outputs/triage_budget_demo.csv",
    "outputs/policy_rag_evaluation.csv",
    "outputs/agent_runs.jsonl",
    "outputs/refund_ledger.jsonl",
]

print("\n1. REQUIRED FILES")
for filename in required_files:
    check(
        f"File: {filename}",
        (ROOT / filename).is_file()
    )

print("\n2. CLEAN DATASETS")
expected_shapes = {
    "data/clean/customers.csv": (1200, 5),
    "data/clean/products.csv": (40, 4),
    "data/clean/orders.csv": (12309, 9),
}

for filename, expected in expected_shapes.items():
    df = pd.read_csv(ROOT / filename)
    check(
        f"{filename} shape",
        df.shape == expected,
        f"actual={df.shape}, expected={expected}"
    )

print("\n3. SQLITE DATABASE")
conn = sqlite3.connect(ROOT / "data/instamart.db")

expected_counts = {
    "customers": 1200,
    "products": 40,
    "orders": 12309,
}

for table, expected in expected_counts.items():
    actual = conn.execute(
        f"SELECT COUNT(*) FROM {table}"
    ).fetchone()[0]

    check(
        f"Database table {table}",
        actual == expected,
        f"rows={actual}"
    )

revenue = conn.execute(
    "SELECT ROUND(SUM(order_amount), 2) "
    "FROM orders WHERE status='completed'"
).fetchone()[0]

check(
    "Completed order revenue",
    revenue == 2998668.80,
    f"INR {revenue:,.2f}"
)

conn.close()

print("\n4. ANALYSIS AND MODEL OUTPUTS")
output_shapes = {
    "outputs/customer_segments.csv": 1175,
    "outputs/retention_list.csv": 10,
    "outputs/triage_results.csv": 164,
    "outputs/triage_budget_demo.csv": 164,
    "outputs/policy_rag_evaluation.csv": 14,
}

for filename, expected_rows in output_shapes.items():
    df = pd.read_csv(ROOT / filename)
    check(
        f"{filename} rows",
        len(df) == expected_rows,
        f"actual={len(df)}, expected={expected_rows}"
    )

print("\n5. POLICY AND AGENT EVALUATION INPUTS")
policy_eval = pd.read_csv(ROOT / "data/raw/policy_eval.csv")
scenarios = pd.read_csv(ROOT / "data/raw/agent_scenarios.csv")

check("Policy evaluation questions", len(policy_eval) == 14)
check("Agent scenarios", len(scenarios) == 7)

print("\n6. AGENT RUNS AND REFUND LEDGER")
agent_path = ROOT / "outputs/agent_runs.jsonl"
ledger_path = ROOT / "outputs/refund_ledger.jsonl"

agent_records = [
    json.loads(line)
    for line in agent_path.read_text(encoding="utf-8").splitlines()
    if line.strip()
]

ledger_records = [
    json.loads(line)
    for line in ledger_path.read_text(encoding="utf-8").splitlines()
    if line.strip()
]

check("Agent run records", len(agent_records) == 7)
check("Refund ledger contains records", len(ledger_records) > 0)

print("\n7. FINAL RESULT")
passed = sum(checks)
total = len(checks)

print(f"\nCHECKS PASSED: {passed}/{total}")

if all(checks):
    print("ALL PROJECT VERIFICATION CHECKS PASSED!")
else:
    raise AssertionError(
        "Some project verification checks failed. Review the FAILED items."
    )
