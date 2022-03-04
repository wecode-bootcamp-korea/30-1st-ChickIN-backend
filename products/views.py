from django.http  import JsonResponse
from django.views import View

from products.models import Product, ProductImage, Option

class ProductDetailView(View):
    def get(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
            images  = ProductImage.objects.filter(product_id=product.id)
            options = Option.objects.all()

            data = {
                    'image'       : [product_image.image_url for product_image in images],
                    'name'        : product.name,
                    'price'       : product.price,
                    'description' : product.description,
                    'option'      : {
                        'name'  : [product_option.name for product_option in options],
                        'price' : [product_option.price for product_option in options]
                    }
                }

            return JsonResponse({'data':[data]}, status=201)

        except Product.DoesNotExist:
            return JsonResponse({'message':'NOT_FOUND'}, status=404)

