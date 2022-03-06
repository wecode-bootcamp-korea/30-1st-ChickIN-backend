import json, uuid

from django.http      import JsonResponse
from django.views     import View
from django.db        import transaction
from django.db.models import F, Sum
from enum             import Enum

from users.models  import User
from users.utils   import login_required
from carts.models  import Cart
from orders.models import Order, OrderItem, OrderOption, OrderStatus

class OrederStatusEnum(Enum):
    PAID            = 1
    PENDING         = 2
    PREPARING       = 3
    SHIPPEND        = 4
    DELIVERD        = 5
    ORDER_CANCELLED = 6

class OrderView(View):
    @login_required
    def post(self, request):
        data  = json.loads(request.body)
        user  = request.user
        items = data

        try:
            with transaction.atomic():
                order = Order.objects.create(
                    order_number = uuid.uuid4(),
                    address      = User.objects.get(id=user.id).address,
                    user         = user,
                    order_status = OrderStatus.objects.get(id=OrederStatusEnum.PENDING.value)
                )

                order_items = [OrderItem(
                    order      = order,
                    product_id = item['product_id'],
                    quantity   = item['quantity'] 
                )for item in items]

                order_options = [OrderOption(
                    option_id = item['option_id'],
                    order_item_id = item['orderitem_id']
                ) for item in items]

                OrderItem.objects.bulk_create(order_items)
                OrderOption.objects.bulk_create(order_options)

                carts = Cart.objects.filter(user=user)
                if carts:
                    carts.delete()

            return JsonResponse({'message':order.id}, status=201)

        except transaction.TransactionManagementError:
            return JsonResponse({'message':'TransactionManagementError'}, status=401)  

    @login_required
    def get(self, request):
        user        = request.user
        order       = request.GET.get('id',)
        order_items = Order.objects.get(id=order).orderitem_set.all()
        total_price = int(Order.objects.filter(id=order)\
                        .annotate(total=Sum(F('orderitem__product__price')*F('orderitem__quantity')))[0].total)
        
        order_list = [{
            'order_id'   : order,
            'user'       : User.objects.get(id=user.id).name,
            'address'    : Order.objects.get(id=order).address,
            'order_items': [{
                'product_id'    : order_item.product.id,
                'quantity'      : order_item.quantity,
                'product_name'  : order_item.product.name,
                'product_image' : order_item.product.thumbnail,
                'price'         : int((order_item.quantity)*(order_item.product.price))
            } for order_item in order_items],
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
        
        except KeyError:
            return JsonResponse({'message':'KEY_ERROR'}, status=400)