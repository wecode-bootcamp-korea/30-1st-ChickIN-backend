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

    @login_required
    def patch(self, request):
        try:
            data = json.loads(request.body)

            with transaction.atomic():
                Order.objects.filter(id=data['order_id']).update(order_status=OrederStatusEnum.ORDER_CANCELLED.value)
                return JsonResponse({'message':'SUCCESS'}, status=200)

        except Order.DoesNotExist:
            return JsonResponse({'message':'NOT_FOUND'}, status=404)

        except KeyError:
            return JsonResponse({'message':'KEY_ERROR'}, status=400)


class OrderNowView(View):
    @login_required
    def post(self, request):
        try:
            data  = json.loads(request.body)
            user  = request.user

            with transaction.atomic():
                order = Order.objects.create(
                    order_number = uuid.uuid4(),
                    address      = user.address,
                    user         = user,
                    order_status = OrderStatus.objects.get(id=OrederStatusEnum.PREPARING.value)
                )

                order_item  = OrderItem.objects.create(
                    order      = order,
                    product_id = data['product_id'],
                    quantity   = data['quantity']
                )

                if data.get('option_id'):
                    OrderOption.objects.create(
                        option_id  = data['option_id'],
                        order_item = order_item
                    )

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

