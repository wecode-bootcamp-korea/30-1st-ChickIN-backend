from django.http  import JsonResponse
from django.views import View

from products.models import Product, Option, ProductOption

class ProductDetailView(View):
    def get(self, request, product_id):
        try:
            product = Product.objects.prefetch_related('productimage_set', 'productoption__option')\
                .get(id=product_id)

            data = {
                    'image'       : [image.image_url for image in product.productimage_set.all()],
                    'name'        : product.name,
                    'price'       : product.price,
                    'description' : product.description,
                    'option'      : [{
                        'name'  : option.name,
                        'price' : option.price
                    } for option in product.productoption__option.all()]
                }

            return JsonResponse({'data':data}, status=200)

        except Product.DoesNotExist:
            return JsonResponse({'message':'NOT_FOUND'}, status=404)

