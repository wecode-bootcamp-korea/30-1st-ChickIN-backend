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

class OrderNowView(View):
    @login_required
    def post(self, request):
        try:
            data  = json.loads(request.body)
            user  = request.user

            with transaction.atomic():
                order = Order.objects.create(
                    order_number    = uuid.uuid4(),
                    address         = user.address,
                    user            = user,
                    order_status_id = OrderStatusEnum.PREPARING.value
                )

                order_item  = OrderItem.objects.create(
                    order      = order,
                    product_id = data['product_id'],
                    quantity   = data['quantity']
                )

                if data.get('option_ids'):
                    order_options = [OrderOption(
                        option_id  = option_id,
                        order_item = order_item
                    ) for option_id in data['option_ids']]
                    
                    OrderOption.objects.bulk_create(order_options)

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

        except JSONDecodeError:
            return JsonResponse({'message':'JSONDecodeError'}, status=400)

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

