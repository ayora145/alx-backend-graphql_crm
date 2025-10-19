import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
django.setup()

from crm.models import Customer, Product, Order

def seed_database():
    # Create customers
    customers = [
        Customer.objects.create(name="Alice Johnson", email="alice@example.com", phone="+1234567890"),
        Customer.objects.create(name="Bob Smith", email="bob@example.com", phone="123-456-7890"),
        Customer.objects.create(name="Carol Davis", email="carol@example.com"),
    ]
    
    # Create products
    products = [
        Product.objects.create(name="Laptop", price=Decimal('999.99'), stock=10),
        Product.objects.create(name="Mouse", price=Decimal('29.99'), stock=50),
        Product.objects.create(name="Keyboard", price=Decimal('79.99'), stock=25),
    ]
    
    # Create orders
    order1 = Order.objects.create(customer=customers[0])
    order1.products.set([products[0], products[1]])
    order1.save()
    
    order2 = Order.objects.create(customer=customers[1])
    order2.products.set([products[1], products[2]])
    order2.save()
    
    print("Database seeded successfully!")

if __name__ == "__main__":
    seed_database()