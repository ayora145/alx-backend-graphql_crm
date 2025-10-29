#!/usr/bin/env python3
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import datetime

GRAPHQL_ENDPOINT = "http://localhost:8000/graphql"
LOG_FILE = "/tmp/order_reminders_log.txt"

def fetch_recent_orders():
    """Fetch orders with order_date within the last 7 days from GraphQL API."""
    transport = RequestsHTTPTransport(url=GRAPHQL_ENDPOINT)
    client = Client(transport=transport, fetch_schema_from_transport=True)
    
    query = gql("""
    query GetRecentOrders($startDate: DateTime!) {
        allOrders(orderDateGte: $startDate) {
            edges {
                node {
                    id
                    customer {
                        email
                    }
                    orderDate
                }
            }
        }
    }
    """)
    
    one_week_ago = (datetime.datetime.now() - datetime.timedelta(days=7)).isoformat()
    result = client.execute(query, variable_values={"startDate": one_week_ago})
    
    orders = []
    if result and "allOrders" in result and "edges" in result["allOrders"]:
        orders = [edge["node"] for edge in result["allOrders"]["edges"]]
    
    return orders

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
