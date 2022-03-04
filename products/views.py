from django.http  import JsonResponse
from django.views import View

from products.models import Product

class ProductDetailView(View):
    def get(self, request, product_id):
        try:
            product = Product.objects.prefetch_related('productimage_set').get(id=product_id)
            options = product.options.filter(product__id=product_id)

            data = {
                    'image'       : [image.image_url for image in product.productimage_set.all()],
                    'name'        : product.name,
                    'price'       : product.price,
                    'description' : product.description,
                    'option'      : [{
                        'name'  : option.name,
                        'price' : option.price
                    } for option in options]
                }

            return JsonResponse({'data':data}, status=200)

        except Product.DoesNotExist:
            return JsonResponse({'message':'NOT_FOUND'}, status=404)

