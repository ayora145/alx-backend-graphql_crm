import datetime
import requests

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
