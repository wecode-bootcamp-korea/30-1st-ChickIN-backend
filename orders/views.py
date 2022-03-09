import json, uuid

from django.http      import JsonResponse
from django.views     import View
from django.db        import transaction
from enum             import Enum

from users.utils   import login_required
from users.models  import User
from carts.models  import Cart
from orders.models import Order, OrderItem, OrderOption, OrderStatus

class OrderView(View):
    @login_required
    def get(self, request):
        user          = request.user
        orders        = Order.objects.filter(user=user)
        
        order_list = [{
            'order_id'   : order.id,
            'user'       : user.username,
            'address'    : order.address,
            'order_items': [{
                'product_id'    : order_item.product.id,
                'quantity'      : order_item.quantity,
                'product_name'  : order_item.product.name,
                'product_image' : order_item.product.thumbnail,
                'price'         : int((order_item.quantity)*(order_item.product.price)),
                'product_options': [{
                    'option_name'  : order_option.option.name,
                    'option_price' : order_option.option.price
                } for order_option in order_item.orderoption_set.all()] 
            }for order_item in order.orderitem_set.all()]
        } for order in orders]

        return JsonResponse({'order_list':order_list}, status=200)