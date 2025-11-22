from django.urls import path

from .views import AddToCartView, CartView, RemoveFromCartView, UpdateQuantityView

urlpatterns = [
    path("add/", AddToCartView.as_view()),
    path("get/", CartView.as_view()),
    path("delete/", RemoveFromCartView.as_view()),
    path("update/", UpdateQuantityView.as_view()),
]
