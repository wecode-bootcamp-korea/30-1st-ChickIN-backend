import json

from django.http      import JsonResponse
from django.views     import View

from users.utils      import login_required
from carts.models     import Cart, CartOption
from products.models  import Option

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
    def post(self, request):
        try:
            data         = json.loads(request.body)
            user         = request.user
            product_id   = data['product_id']
            quantity     = int(data['quantity'])

            if quantity < 1:
                return JsonResponse({'message': 'INVALID_QUANTITY'}, status=400)
            
            cart, created_cart = Cart.objects.get_or_create(
                user_id    = user.id,
                product_id = product_id,
                quantity   = quantity,
            )
            
            cart_get = Cart.objects.get(user_id = user.id)
            # options  = Option.objects.getlist(user_id = request.user.id)
            
            cartoption, created_option = CartOption.objects.get_or_create(
                cart_id    = cart_get.id,
                option_id  = data['option_id']
                # option_id  = [{
                #     'option_id' : option.id
                # }for option in options]
            )
            
            if created_cart and created_option:
                cart.quantity = quantity
            else:
                cart.quantity += quantity
            
            cart.save()
            cartoption.save()

            return JsonResponse({"message" : "SUCCESS"}, status=201) 
        except KeyError:
            return JsonResponse({"message" : "KEY ERROR"}, status=400)
