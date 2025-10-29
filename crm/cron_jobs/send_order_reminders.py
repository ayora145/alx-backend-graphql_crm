#!/usr/bin/env python3
import requests
import datetime
import sys

GRAPHQL_ENDPOINT = "http://localhost:8000/graphql"
LOG_FILE = "/tmp/order_reminders_log.txt"

def fetch_recent_orders():
    """Fetch orders with order_date within the last 7 days from GraphQL API."""
    query = """
    query GetRecentOrders($startDate: DateTime!) {
        orders(orderDate_Gte: $startDate) {
            id
            customer {
                email
            }
            orderDate
        }
    }
    """
    one_week_ago = (datetime.datetime.now() - datetime.timedelta(days=7)).isoformat()
    response = requests.post(
        GRAPHQL_ENDPOINT,
        json={"query": query, "variables": {"startDate": one_week_ago}},
    )

    if response.status_code != 200:
        print(f"GraphQL query failed with status {response.status_code}", file=sys.stderr)
        return []

    data = response.json()
    return data.get("data", {}).get("orders", [])

def log_order_reminders(orders):
    """Log each order’s ID and customer email with timestamp."""
    with open(LOG_FILE, "a") as f:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for order in orders:
            order_id = order["id"]
            email = order["customer"]["email"]
            f.write(f"[{timestamp}] Order ID: {order_id}, Email: {email}\n")

def main():
    orders = fetch_recent_orders()
    if orders:
        log_order_reminders(orders)
    print("Order reminders processed!")

if __name__ == "__main__":
    main()
