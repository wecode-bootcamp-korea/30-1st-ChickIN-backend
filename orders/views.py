import json, uuid

from django.http      import JsonResponse
from django.views     import View
from django.db        import transaction
from django.db.models import F, Sum
from enum             import Enum

from users.utils   import login_required
from users.models  import User
from carts.models  import Cart, CartOption
from orders.models import Order, OrderItem, OrderOption, OrderStatus

class OrederStatusEnum(Enum):
    PAID            = 1
    PREPARING       = 2
    SHIPPEND        = 3
    DELIVERD        = 4
    ORDER_CANCELLED = 5

class OrderView(View):
    @login_required
    def post(self, request):
        data     = json.loads(request.body)
        user     = request.user
        cart_ids = data['cart_ids']
        carts    = Cart.objects.filter(id__in=cart_ids, user=user)

        try:
            if not carts.exists():
                return JsonResponse({'message':'NOT_FOUND'}, status=404)

            with transaction.atomic():
                order = Order.objects.create(
                    order_number = uuid.uuid4(),
                    address      = User.objects.get(id=user.id).address,
                    user         = user,
                    order_status = OrderStatus.objects.get(id=OrederStatusEnum.PREPARING.value)
                )

                order_items = [OrderItem(
                    order      = order,
                    product    = cart.product,
                    quantity   = cart.quantity 
                )for cart in carts]
                OrderItem.objects.bulk_create(order_items)

                cart_options = CartOption.objects.filter(cart__in=cart_ids)
                order_options = [OrderOption(
                    option     = cart_option.option,
                    order_item = OrderItem.objects.get(order_id=order)
                ) for cart_option in cart_options]
                carts.delete()
                OrderOption.objects.bulk_create(order_options)

            return JsonResponse({'message':order.id}, status=201)

        except transaction.TransactionManagementError:
            return JsonResponse({'message':'TransactionManagementError'}, status=401)  
