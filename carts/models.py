from django.db       import models

from users.models    import User
from products.models import Product

class Cart(models.Model):
    quantity   = models.IntegerField()
    user       = models.ForeignKey('User', on_delete=models.CASCADE)
    product    = models.ForeignKey('Product', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'carts'


class CartOption(models.Model):
    option = models.ForeignKey('Option', on_delete=models.CASCADE)
    cart   = models.ForeignKey('Cart', on_delete=models.CASCADE)

    class Meta:
        db_table = 'cart_options'
