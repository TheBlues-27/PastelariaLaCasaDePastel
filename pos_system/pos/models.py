from django.db import models

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('tradicional', 'Sabores Tradicionais'),
        ('acompanhamento', 'Acompanhamentos'),
        ('especial', 'Sabores Especiais'),
        ('doce', 'Sabores Doces'),
        ('bebida', 'Bebidas'),
    ]
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='tradicional')

    def __str__(self):
        return self.name

class Order(models.Model):
    table_number = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'Pedido {self.id} - Mesa {self.table_number}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # price at time of sale

    def __str__(self):
        return f'{self.quantity}x {self.product.name} (Pedido {self.order.id})'