# ALX Backend GraphQL CRM

A Django-based CRM system with GraphQL API for managing customers, products, and orders.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

3. Create superuser:
```bash
python manage.py createsuperuser
```

4. Seed database (optional):
```bash
python seed_db.py
```

5. Run server:
```bash
python manage.py runserver
```

## GraphQL Endpoint

Access GraphiQL at: `http://localhost:8000/graphql`

## Example Queries

### Basic Query
```graphql
{
  hello
}
```

### Create Customer
```graphql
mutation {
  createCustomer(input: {
    name: "Alice",
    email: "alice@example.com",
    phone: "+1234567890"
  }) {
    customer {
      id
      name
      email
      phone
    }
    message
  }
}
```

### Filter Customers
```graphql
query {
  allCustomers(filter: { nameIcontains: "Ali" }) {
    edges {
      node {
        id
        name
        email
      }
    }
  }
}
```