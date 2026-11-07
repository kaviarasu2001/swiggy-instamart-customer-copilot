
import sqlite3
import pandas as pd

DB_PATH = "data/instamart.db"

conn = sqlite3.connect(DB_PATH)

checks = []

# Check 1: Customer count
checks.append(
    conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0] == 1200
)

# Check 2: Product count
checks.append(
    conn.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 40
)

# Check 3: Order count
checks.append(
    conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 12309
)

# Check 4: Completed orders
checks.append(
    conn.execute(
        "SELECT COUNT(*) FROM orders WHERE status='completed'"
    ).fetchone()[0] == 11110
)

# Check 5: Cancelled orders
checks.append(
    conn.execute(
        "SELECT COUNT(*) FROM orders WHERE status='cancelled'"
    ).fetchone()[0] == 1199
)

# Check 6: Completed revenue
revenue = conn.execute(
    "SELECT ROUND(SUM(order_amount), 2) FROM orders "
    "WHERE status='completed'"
).fetchone()[0]

checks.append(revenue == 2998668.80)

# Check 7: No missing order amounts
checks.append(
    conn.execute(
        "SELECT COUNT(*) FROM orders WHERE order_amount IS NULL"
    ).fetchone()[0] == 0
)

# Check 8: No missing completed delivery times
checks.append(
    conn.execute(
        "SELECT COUNT(*) FROM orders "
        "WHERE status='completed' AND delivery_minutes IS NULL"
    ).fetchone()[0] == 0
)

conn.close()

print("DATABASE VALIDATION")
print("=" * 45)

for i, result in enumerate(checks, start=1):
    print(f"Checkpoint {i}: {'PASSED' if result else 'FAILED'}")

if all(checks):
    print("\\nALL CHECKPOINTS PASSED")
else:
    raise AssertionError("Some validation checkpoints failed.")
