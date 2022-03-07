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
                    order_status = OrederStatusEnum.PREPARING.value
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
                    "data" : {
                        "order_id" : order.id,
                        "order_number" : order.order_number
                    }
                }
            return JsonResponse(response, status=201)

        except transaction.TransactionManagementError:
            return JsonResponse({'message':'TransactionManagementError'}, status=400)  

class OrderNowView(View):
    def post(self, request):
        """
        즉시 구매
        
        주의 사항
        1. cart 정보가 없다
        2. product_id랑 option의 정보를 직접 받아서 구현
        """