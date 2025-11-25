from django.urls import path

from .views import (
    AddToCartView,
    CartView,
    RemoveFromCartView,
    UpdateQuantityView,
    SetQuantityView,
    CartPromoView,
    CheckoutPromoView,
)

urlpatterns = [
    path("add/", AddToCartView.as_view()),
    path("get/", CartView.as_view()),
    path("delete/", RemoveFromCartView.as_view()),
    path("update/", UpdateQuantityView.as_view()),
    path("update/quantity", SetQuantityView.as_view()),
    path("promo/", CartPromoView.as_view()),
    path("checkout/", CheckoutPromoView.as_view()),
]
