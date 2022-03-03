from django.db import models

from users.models import User
from products.models import Product, Option


class Order(models.Model):
    order_number = models.UUIDField()
    address      = models.CharField(max_length=200)
    user         = models.ForeignKey('User', on_delete=models.CASCADE)
    order_status = models.ForeignKey('OrderStatus', on_delete=models.CASCADE)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orders'


class OrderItem(models.Model):
    quantity = models.IntegerField()  
    product  = models.ForeignKey('Product', on_delete=models.CASCADE)
    order    = models.ForeignKey('Order', on_delete=models.CASCADE)

    class Meta:
        db_table = 'order_items'


class OrderOption(models.Model):
    option     = models.ForeignKey('Option', on_delete=models.CASCADE)
    order_item = models.ForeignKey('OrderItem', on_delete=models.CASCADE)

    class Meta:
        db_table = 'order_options'


class OrderStatus(models.Model):
    status = models.CharField(max_length=45)

    class Meta:
        db_table = 'order_statuses'
