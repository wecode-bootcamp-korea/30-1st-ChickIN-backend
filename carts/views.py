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
    
    @login_required
    def patch(self, request):
        try:
            data     = json.loads(request.body)
            user     = request.user.id
            cart_id  = data['cart_id']
            quantity = data["quantity"]
            cart     = Cart.objects.get(id=cart_id, user_id=user)

            cart.quantity = quantity
            cart.save()

            return JsonResponse({"message":"SUCCESS"}, status=201)
        except KeyError:
            return JsonResponse({"message":"KEY ERROR"}, status=401)
    