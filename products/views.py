from django.http  import JsonResponse
from django.views import View

from products.models import Product

class ProductDetailView(View):
    def get(self, request, product_id):
        try:
            product = Product.objects.prefetch_related('productimage_set').get(id=product_id)
            options = product.options.all()

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

class ProductListView(View):
    def get(self, request):
        try:
            main_category = request.GET.get('main_category', None)
            sub_category  = request.GET.get('sub_category', None)
            searching     = request.GET.get('name', None)

            product_list  = []
            products = Product.objects.all()
            products = SubCategory.objects.prefetch_related('product_set').filter(main_category_id=main_category)\
        	   if main_category else products
            products = Product.objects.select_related('sub_category').filter(sub_category_id=sub_category)\
        	   if sub_category else products
            products = Product.objects.filter(name__icontains=searching) if searching else products

            if main_category:
                for product in products:
                    product = product.product_set.all()
                    for item in product:
                        product_list.append({
                            'thumbnail'   : item.thumbnail,
                            'name'        : item.name,
                            'price'       : item.price
                        })

            else:
                for product in products:
                    product_list.append(
                        {
                            'thumbnail'    : product.thumbnail,
                            'name'         : product.name,
                            'price'        : product.price
                        }
                    )

            return JsonResponse({'products_list':product_list}, status=200)

        except Product.DoesNotExist:
            return JsonResponse({'message':'NOT_FOUND'}, status=404)
        
        except AttributeError:
            return JsonResponse({'message':'AttributeError'}, status=400)
        
        except TypeError:
            return JsonResponse({'message':'TypeError'}, status=400)
