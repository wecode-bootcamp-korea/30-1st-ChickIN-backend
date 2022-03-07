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

    @login_required
    def get(self, request):
        user          = request.user
        order         = request.GET.get('id',)
        order_items   = Order.objects.get(id=order).orderitem_set.all()
        order_options = OrderItem.objects.get(order_id=order).orderoption_set.all()
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
                'price'         : int((order_item.quantity)*(order_item.product.price))
            } for order_item in order_items],
            'product_options': [{
                'option_name'  : order_option.option.name,
                'option_price' : order_option.option.price
            } for order_option in order_options],
            'total_price' : total_price
        }]

        return JsonResponse({'order_list':order_list}, status=200)

    @login_required
    def patch(self, request):
        data     = json.loads(request.body)
        order_id = data['order_id']

        try:
            Order.objeccts.filter(id=order_id).update(order_status=OrederStatusEnum.ORDER_CANCELLED.value)
            return JsonResponse({'message':'SUCCESS'}, status=200)

        except Order.DoesNotExist:
            return JsonResponse({'message':'NOT_FOUND'}, status=404)

        except KeyError:
            return JsonResponse({'message':'KEY_ERROR'}, status=400)
