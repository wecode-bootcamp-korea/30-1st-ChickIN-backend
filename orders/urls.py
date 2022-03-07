from django.urls import path

from orders.views import OrderNowView

urlpatterns = [
    path('/ordernow', OrderNowView.as_view())
]