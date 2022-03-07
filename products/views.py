from django.http      import JsonResponse
from django.views     import View
from django.db.models import Q

from products.models import Product

class ProductListView(View):
    def get(self, request):
        main_category = request.GET.get('main_category')
        sub_category  = request.GET.get('sub_category')
        searching     = request.GET.get('name')
        sort          = request.GET.get('sort', 'id')
        limit         = int(request.GET.get('limit', 36))
        offset        = int(request.GET.get('offset', 0))

        q = Q()
            
        if main_category:
            q &= Q(sub_category__main_category_id=main_category)

        if sub_category:
            q &= Q(sub_category_id=sub_category)

        if searching:
            q &= Q(name__icontains=searching)

        sort_type = {
            'id'   : 'id',
            'rec'  : '?',
            'desc' : '-price',
            'asc'  : 'price'
        }

        products = Product.objects.select_related('sub_category')\
            .filter(q).order_by(sort_type[sort])[offset:offset+limit]

        product_list = [{
            'thumbnail' : product.thumbnail,
            'name'      : product.name,
            'price'     : product.price
        } for product in products]

        return JsonResponse({'products_list':product_list}, status=200)

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