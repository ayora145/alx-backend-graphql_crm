#!/bin/bash

# Deletes customers with no orders in the past year and logs the count.

# Move to project directory
cd "$(dirname "$0")" || exit

# Run Django shell command
deleted_count=$(python3 manage.py shell -c "
from datetime import timedelta
from django.utils import timezone
from crm.models import Customer
one_year_ago = timezone.now() - timedelta(days=365)
deleted, _ = Customer.objects.filter(orders__isnull=True, date_joined__lt=one_year_ago).delete()
print(deleted)
")

# Log with timestamp
timestamp=$(date '+%Y-%m-%d %H:%M:%S')
echo \"[\$timestamp] Deleted customers: \$deleted_count\" >> /tmp/customer_cleanup_log.txt
