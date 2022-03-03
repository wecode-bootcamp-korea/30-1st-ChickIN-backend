from django.db       import models

class Cart(models.Model):
    quantity   = models.IntegerField()
    user       = models.ForeignKey('users.User', on_delete=models.CASCADE)
    product    = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'carts'


class CartOption(models.Model):
    option = models.ForeignKey('products.Option', on_delete=models.CASCADE)
    cart   = models.ForeignKey('carts.Cart', on_delete=models.CASCADE)

    class Meta:
        db_table = 'cart_options'
