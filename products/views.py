from django.http      import JsonResponse
from django.views     import View
from django.db.models import Q

from products.models import Product, SubCategory

class ProductListView(View):
    def get(self, request):
        try:
            main_category = request.GET.get('main_category', None)
            sub_category  = request.GET.get('sub_category', None)
            searching     = request.GET.get('name', None)
            limit         = int(request.GET.get('limit', 36))
            offset        = int(request.GET.get('offset', 0))
            
            q = Q()
            products = Product.objects.all()
            products = SubCategory.objects.prefetch_related('product_set').filter(main_category_id=main_category)[offset:offset+limit]\
        	   if main_category else products

            if sub_category:
                q &= Q(sub_category_id=sub_category)
            if searching:
                q &= Q(name__icontains=searching)
            products = Product.objects.select_related('sub_category').filter(q)[offset:offset+limit]\
                if sub_category or searching else products

            product_list = []
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
                product_list = [{
                            'thumbnail' : product.thumbnail,
                            'name'      : product.name,
                            'price'     : product.price
                        } for product in products]

            return JsonResponse({'products_list':product_list}, status=200)

        except Product.DoesNotExist:
            return JsonResponse({'message':'NOT_FOUND'}, status=404)
        
        except AttributeError:
            return JsonResponse({'message':'AttributeError'}, status=400)


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

