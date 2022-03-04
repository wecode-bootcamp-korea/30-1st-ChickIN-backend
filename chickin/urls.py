from django.urls import path, include

urlpatterns = [
    path('carts',    include('carts.urls')),
    path('orders',   include('orders.urls')),
    path('products', include('products.urls')),
    path('users',    include('users.urls')),
]