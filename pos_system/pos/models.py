from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    category = models.CharField(max_length=50) # e.g., 'tradicional', 'especial', 'acompanhamento'

    def __str__(self):
        return self.name

class Order(models.Model):
    table_number = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Order {self.id} - Table {self.table_number} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    name = models.CharField(max_length=100) # Store name in case product is deleted
    price = models.DecimalField(max_digits=6, decimal_places=2) # Store price at time of order
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.name} (Order {self.order.id})"

class AccompanimentItem(models.Model):
    order_item = models.ForeignKey(OrderItem, related_name='accompaniments', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    name = models.CharField(max_length=100) # Store name in case product is deleted
    price = models.DecimalField(max_digits=6, decimal_places=2) # Store price at time of order
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.name} (for {self.order_item.name})"