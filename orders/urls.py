from django.urls import path

from orders.views import OrderView, OrderNowView

urlpatterns = [
    path('', OrderView.as_view()),
    path('/ordernow', OrderNowView.as_view())
]