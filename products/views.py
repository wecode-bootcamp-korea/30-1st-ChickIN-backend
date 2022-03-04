from django.http  import JsonResponse
from django.views import View

from products.models import Product, ProductImage, Option

class ProductDetailView(View):
    def get(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
            images  = product.productimage_set.all()
            options = product.productoption_set.all()

            data = {
                    'image'       : [image.image_url for image in images],
                    'name'        : product.name,
                    'price'       : product.price,
                    'description' : product.description,
                    'option'      : {
                        'name'  : [option.name for option in options],
                        'price' : [option.price for option in options]
                    }
                }

            return JsonResponse({'data':data}, status=200)

        except Product.DoesNotExist:
            return JsonResponse({'message':'NOT_FOUND'}, status=404)

