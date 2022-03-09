import json, uuid

from django.http      import JsonResponse
from django.views     import View
from django.db        import transaction
from json             import JSONDecodeError
from enum             import Enum

from users.utils   import login_required
from carts.models  import Cart
from orders.models import Order, OrderItem, OrderOption

class OrderStatusEnum(Enum):
    PAID            = 1
    PREPARING       = 2
    SHIPPEND        = 3
    DELIVERD        = 4
    ORDER_CANCELLED = 5

class OrderView(View):
    @login_required
    def patch(self, request, order_id):
        try:
            data   = json.loads(request.body)
            user   = request.user
            status = data['status']

            order_status = {
                'paid'            : OrderStatusEnum.PAID.value,
                'preparing'       : OrderStatusEnum.PREPARING.value,
                'shippend'        : OrderStatusEnum.SHIPPEND.value,
                'deliverd'        : OrderStatusEnum.DELIVERD.value,
                'order_cancelled' : OrderStatusEnum.ORDER_CANCELLED.value
            }

            order = Order.objects.get(user=user, order_id=order_id)

            order.order_status = order_status[status]
            order.save()

            return JsonResponse({'message':'SUCCESS'}, status=200)

        except Order.DoesNotExist:
            return JsonResponse({'message':'NOT_FOUND'}, status=404)

        except KeyError:
            return JsonResponse({'message':'KEY_ERROR'}, status=400)
