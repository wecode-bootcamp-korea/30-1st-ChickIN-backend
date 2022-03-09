import json

from django.http      import JsonResponse
from django.views     import View
from django.db        import transaction

from users.utils      import login_required
from carts.models     import Cart, CartOption
from products.models  import Option

class CartView(View):
    @login_required
    def post(self, request):
        try:
            data       = json.loads(request.body)
            user       = request.user
            product_id = data['product_id']
            option_ids = data['option_ids'] 
            options    = Option.objects.filter(id__in=option_ids)
            quantity   = int(data['quantity'])
            is_added   = False

            if quantity < 1:
                return JsonResponse({'message': 'INVALID_QUANTITY'}, status=400)
            
            with transaction.atomic():
                for cart in Cart.objects.filter(product_id=product_id, user=user):
                    cart_options = Option.objects.filter(cartoption__cart=cart)
                    
                    if set(cart_options) == set(options):
                        is_added = True
                        break
                    
                if is_added:
                    cart.quantity += quantity
                    cart.save()
                    return JsonResponse({"message" : "SUCCESS"}, status=200)
                
                cart = Cart.objects.create(
                    user_id    = user.id,
                    product_id = product_id,
                    quantity   = quantity,
                )
                
                cart_options =[CartOption(
                    cart_id   = cart.id,
                    option_id = option.id,
                )for option in options]
                
                CartOption.objects.bulk_create(cart_options)

            return JsonResponse({"message" : "SUCCESS"}, status=201) 
        except KeyError:
            return JsonResponse({"message" : "KEY ERROR"}, status=400)
        except transaction.TransactionManagementError:
            return JsonResponse({"message" : "TransactionManagementError"}, status=400)