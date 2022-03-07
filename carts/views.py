import json

from django.http      import JsonResponse
from django.views     import View

from users.utils      import login_required
from carts.models     import Cart

class CartView(View):
    @login_required
    def get(self, request):
        carts = Cart.objects.filter(user_id = request.user.id)
        result = [{
                'cart_id'    : cart.id,
                'user_id'    : request.user.id,
                'quantity'   : cart.quantity,
                'product'    :{
                    'name'       : cart.product.name,
                    'thumbnail'  : cart.product.thumbnail,
                    'price'      : int(cart.product.price),
                    },
                'option'     : [{
                    'name'  : cart_option.option.name,
                    'price' : cart_option.option.price,
                    }for cart_option in cart.cartoption_set.all()],
                } for cart in carts]

        return JsonResponse({'result' : result}, status=200)