from django.db       import models

from users.models    import User
from products.models import Product

class Cart(models.Model):
    quantity   = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user_id    = models.ForeignKey('User', on_delete=models.CASCADE)
    product_id = models.ForeignKey('Product', on_delete=models.CASCADE)

    class Meta:
        db_table = 'carts'


class CartOption(models.Model):
    product_id = models.ForeignKey('Product', on_delete=models.CASCADE)
    cart_id    = models.ForeignKey('Cart', on_delete=models.CASCADE)

    class Meta:
        db_table = 'cart_options'
