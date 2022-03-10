from django.urls import path

from orders.views import OrderView, OrderNowView

urlpatterns = [
    path('', OrderView.as_view()),
    path('/now', OrderNowView.as_view())
]