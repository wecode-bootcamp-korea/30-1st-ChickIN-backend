from django.urls import path

from products.views import ProductView

urlpatterns = [
    path('/productlist', ProductView.as_view()),
]