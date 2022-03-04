from django.http      import JsonResponse
from django.views     import View
from django.db.models import Q

from products.models import SubCategory, Product, ProductImage, Option

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