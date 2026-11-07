
import sqlite3
import pandas as pd

DB_PATH = "/content/instamart-copilot-workspace/Instamart_DB.db"

def run_eda():

    connection = sqlite3.connect(DB_PATH)

    queries = {
        "Customers by City": """
            SELECT city, COUNT(*) AS total_customers
            FROM customers
            GROUP BY city
            ORDER BY total_customers DESC
        """,

        "Orders by Status": """
            SELECT order_status, COUNT(*) AS total_orders
            FROM orders
            GROUP BY order_status
            ORDER BY total_orders DESC
        """,

        "Payment Methods": """
            SELECT payment_method, COUNT(*) AS total_orders
            FROM orders
            GROUP BY payment_method
            ORDER BY total_orders DESC
        """,

        "Revenue by City": """
            SELECT c.city,
                   COUNT(o.order_id) AS total_orders,
                   ROUND(SUM(o.order_amount), 2) AS total_revenue
            FROM customers c
            JOIN orders o
            ON c.customer_id = o.customer_id
            GROUP BY c.city
            ORDER BY total_revenue DESC
        """,

        "Support Ticket Categories": """
            SELECT issue_category, COUNT(*) AS total_tickets
            FROM tickets
            GROUP BY issue_category
            ORDER BY total_tickets DESC
        """
    }

    for title, query in queries.items():

        print("\n" + "=" * 50)
        print(title.upper())
        print("=" * 50)

        result = pd.read_sql_query(query, connection)

        print(result.to_string(index=False))

    connection.close()


if __name__ == "__main__":
    run_eda()
