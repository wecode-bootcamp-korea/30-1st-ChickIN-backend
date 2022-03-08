import json
from statistics import quantiles

from django.http      import JsonResponse
from django.views     import View

from users.utils      import login_required
from carts.models     import Cart

class CartView(View):
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
