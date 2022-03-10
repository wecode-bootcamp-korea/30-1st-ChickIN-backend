from django.urls import path

from orders.views import OrderNowView

urlpatterns = [
    path('/now', OrderNowView.as_view())
]