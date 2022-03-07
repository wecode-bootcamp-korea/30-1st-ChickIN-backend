import json, uuid

from django.http      import JsonResponse
from django.views     import View
from django.db        import transaction
from django.db.models import F, Sum
from enum             import Enum

from users.utils   import login_required
from users.models  import User
from carts.models  import Cart
from orders.models import Order, OrderItem, OrderOption, OrderStatus

class OrderView(View):
    @login_required
    def get(self, request):
        user          = request.user
        order         = request.GET.get('id',)
        order_items   = OrderItem.objects.filter(order_id=order)
        order_options = OrderOption.objects.filter(order_item__order_id=order)

        if order_options:
            total_price   = int(Order.objects.filter(id=order)\
                            .annotate(total=Sum(F('orderitem__product__price')*F('orderitem__quantity')\
                                +F('orderitem__orderoption__option__price')))[0].total)
                                
        else:
            total_price   = int(Order.objects.filter(id=order)\
                            .annotate(total=Sum(F('orderitem__product__price')*F('orderitem__quantity')))[0].total)
        
        order_list = [{
            'order_id'   : order,
            'user'       : User.objects.get(id=user.id).username,
            'address'    : Order.objects.get(id=order).address,
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
            }for order_item in order_items],
            'total_price' : total_price
        }]

        return JsonResponse({'order_list':order_list}, status=200)