import json, uuid

from django.http      import JsonResponse
from django.views     import View
from django.db        import transaction
from json             import JSONDecodeError
from enum             import Enum

from users.utils   import login_required
from carts.models  import Cart
from orders.models import Order, OrderItem, OrderOption

class OrederStatusEnum(Enum):
    PAID            = 1
    PREPARING       = 2
    SHIPPEND        = 3
    DELIVERD        = 4
    ORDER_CANCELLED = 5

class OrderView(View):
    @login_required
    def post(self, request):
        try:
            data     = json.loads(request.body)
            user     = request.user
            cart_ids = data['cart_ids']
            carts    = Cart.objects.filter(id__in=cart_ids, user=user)

            if not carts.exists():
                return JsonResponse({'message':'NOT_FOUND'}, status=404)

            with transaction.atomic():
                order = Order.objects.create(
                    order_number = uuid.uuid4(),
                    address      = user.address,
                    user         = user,
                    order_status = OrderStatus.objects.get(id=OrederStatusEnum.PREPARING.value)
                )
                for cart in carts:
                    order_item = OrderItem.objects.create(
                        order      = order,
                        product    = cart.product,
                        quantity   = cart.quantity 
                    )

                    cart_options  = cart.cartoption_set.all()
                    order_options = [OrderOption(
                        option     = cart_option.option,
                        order_item = order_item
                    ) for cart_option in cart_options]

                    OrderOption.objects.bulk_create(order_options)

                carts.delete()
                response = {
                    "message" : "created",
                    "data"    : {
                        "order_id"     : order.id,
                        "order_number" : order.order_number
                    }
                }
            return JsonResponse(response, status=201)

        except transaction.TransactionManagementError:
            return JsonResponse({'message':'TransactionManagementError'}, status=400)  
          
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

            order = Order.objects.get(user=user, id=order_id)

            order.order_status_id = order_status[status]
            order.save()

            return JsonResponse({'message':'SUCCESS'}, status=200)

        except Order.DoesNotExist:
            return JsonResponse({'message':'NOT_FOUND'}, status=404)

        except KeyError:
            return JsonResponse({'message':'KEY_ERROR'}, status=400)       
