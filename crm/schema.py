import graphene
from graphene_django import DjangoObjectType, DjangoFilterConnectionField
from graphene_django.filter import DjangoFilterConnectionField
from django.core.exceptions import ValidationError
from django.db import transaction
from decimal import Decimal
import re
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        filterset_class = CustomerFilter
        interfaces = (graphene.relay.Node,)

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        filterset_class = ProductFilter
        interfaces = (graphene.relay.Node,)

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        filterset_class = OrderFilter
        interfaces = (graphene.relay.Node,)

# Input Types
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int()

class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()

# Mutations
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, input):
        # Validate phone format
        if input.phone and not re.match(r'^\+?[\d\-\(\)\s]+$', input.phone):
            raise ValidationError("Invalid phone format")
        
        try:
            customer = Customer.objects.create(
                name=input.name,
                email=input.email,
                phone=input.phone
            )
            return CreateCustomer(customer=customer, message="Customer created successfully")
        except Exception as e:
            raise ValidationError(f"Error creating customer: {str(e)}")

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        customers = []
        errors = []
        
        with transaction.atomic():
            for customer_data in input:
                try:
                    if customer_data.phone and not re.match(r'^\+?[\d\-\(\)\s]+$', customer_data.phone):
                        errors.append(f"Invalid phone format for {customer_data.name}")
                        continue
                    
                    customer = Customer.objects.create(
                        name=customer_data.name,
                        email=customer_data.email,
                        phone=customer_data.phone
                    )
                    customers.append(customer)
                except Exception as e:
                    errors.append(f"Error creating {customer_data.name}: {str(e)}")
        
        return BulkCreateCustomers(customers=customers, errors=errors)

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)

    def mutate(self, info, input):
        if input.price <= 0:
            raise ValidationError("Price must be positive")
        
        if input.stock is not None and input.stock < 0:
            raise ValidationError("Stock cannot be negative")
        
        product = Product.objects.create(
            name=input.name,
            price=input.price,
            stock=input.stock or 0
        )
        return CreateProduct(product=product)

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)

    def mutate(self, info, input):
        try:
            customer = Customer.objects.get(id=input.customer_id)
        except Customer.DoesNotExist:
            raise ValidationError("Customer not found")
        
        if not input.product_ids:
            raise ValidationError("At least one product is required")
        
        products = Product.objects.filter(id__in=input.product_ids)
        if len(products) != len(input.product_ids):
            raise ValidationError("One or more products not found")
        
        order = Order.objects.create(customer=customer)
        order.products.set(products)
        order.save()  # This will calculate total_amount
        
        return CreateOrder(order=order)

class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")
    
    all_customers = DjangoFilterConnectionField(CustomerType, filterset_class=CustomerFilter)
    all_products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter)
    all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter)
    
    customer = graphene.Field(CustomerType, id=graphene.ID())
    product = graphene.Field(ProductType, id=graphene.ID())
    order = graphene.Field(OrderType, id=graphene.ID())

    def resolve_customer(self, info, id):
        return Customer.objects.get(id=id)

    def resolve_product(self, info, id):
        return Product.objects.get(id=id)

    def resolve_order(self, info, id):
        return Order.objects.get(id=id)

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()