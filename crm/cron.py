import datetime
import requests

def update_low_stock():
    """Updates low stock products via GraphQL mutation and logs the results."""
    log_file = "/tmp/low_stock_updates_log.txt"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    mutation = """
    mutation {
        updateLowStockProducts {
            updatedProducts {
                name
                stock
            }
            message
        }
    }
    """
    
    try:
        response = requests.post(
            "http://localhost:8000/graphql",
            json={"query": mutation},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if "data" in data and "updateLowStockProducts" in data["data"]:
                updated_products = data["data"]["updateLowStockProducts"]["updatedProducts"]
                
                with open(log_file, "a") as f:
                    for product in updated_products:
                        f.write(f"[{timestamp}] Updated {product['name']} - New stock: {product['stock']}\n")
                    
                    if not updated_products:
                        f.write(f"[{timestamp}] No low stock products found\n")
            else:
                with open(log_file, "a") as f:
                    f.write(f"[{timestamp}] GraphQL mutation failed: {data}\n")
        else:
            with open(log_file, "a") as f:
                f.write(f"[{timestamp}] HTTP error {response.status_code}\n")
    
    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"[{timestamp}] Error updating low stock: {e}\n")

def log_crm_heartbeat():
    """Logs a heartbeat message every 5 minutes to confirm CRM health."""
    log_file = "/tmp/crm_heartbeat_log.txt"
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{timestamp} CRM is alive\n"

    try:
        # Optional: check if the GraphQL API is responsive
        response = requests.post(
            "http://localhost:8000/graphql",
            json={"query": "{ hello }"},
            timeout=5
        )
        if response.status_code == 200:
            message = f"{timestamp} CRM is alive and GraphQL responded successfully\n"
        else:
            message = f"{timestamp} CRM is alive but GraphQL returned {response.status_code}\n"
    except Exception as e:
        message = f"{timestamp} CRM heartbeat failed to contact GraphQL: {e}\n"

    # Append to the log file (do not overwrite)
    with open(log_file, "a") as f:
        f.write(message)
