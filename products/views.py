from django.http  import JsonResponse
from django.views import View

from products.models import Purchase, MainCategory, SubCategory, Product, ProductImage, ProductOption

class ProductView(View):
    def get(self, request):
        products      = Product.objects.all()
        products_list = []

        for product in products:
            products_list.append(
                {
                    "name" : product.name,
                    "price" : product.price,
                    "description" : product.description,
                    "thumbnail" : product.thumbnail,
                    "sub_category" : SubCategory.objects.get(id = product.sub_category_id).name
                }
            )

        return JsonResponse({"products_list":products_list}, status=200)