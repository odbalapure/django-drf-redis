from rest_framework.views import APIView
from .serializer import (
    AddToCartSerializer,
    CartItemSerializer,
    RemoveFromCartSerializer,
    UpdateQuantitySerializer,
)
from .redis_cart import (
    add_to_cart,
    get_cart,
    remove_from_cart,
    clear_cart,
    increment_quantity,
    decrement_quantity,
)
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema


# Get, clear cart
class CartView(APIView):
    @extend_schema(
        responses={200: CartItemSerializer(many=True)}, description="Get cart products"
    )
    def get(self, request):
        session_id = request.session.session_key
        cart_data = get_cart(session_id)
        return Response(cart_data)

    def delete(self, request):
        session_id = request.session.session_key
        clear_cart(session_id)
        return Response({"message": "Cart cleared"}, status=status.HTTP_204_NO_CONTENT)


# Create your views here.
class AddToCartView(APIView):
    @extend_schema(
        request=AddToCartSerializer,
        responses={200: None},
        description="Add a product to the cart",
    )
    def post(self, request):
        if not request.session.session_key:
            request.session.create()
        session_id = request.session.session_key

        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # product_id = serializer.validated_data["product_id"]
        # name = serializer.validated_data["name"]
        # price = serializer.validated_data["price"]
        # quantity = serializer.validated_data["quantity"]
        data = serializer.validated_data

        add_to_cart(
            session_id,
            product_id=data["product_id"],
            name=data["name"],
            price=data["price"],
            quantity=data["quantity"],
        )

        return Response({"message": "Added to cart."}, status=status.HTTP_200_OK)


# Remove from cart
class RemoveFromCartView(APIView):
    @extend_schema(
        request=RemoveFromCartSerializer,
        responses={204: None},
        description="Remove product from current cart session",
    )
    def post(self, request):
        session_id = request.session.session_key
        serializer = RemoveFromCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data["product_id"]
        remove_from_cart(session_id, product_id)

        return Response(status=status.HTTP_204_NO_CONTENT)


class UpdateQuantityView(APIView):
    @extend_schema(
        request=UpdateQuantitySerializer,
        responses={200: None},
        description="Update product quantity",
    )
    def post(self, request):
        session_id = request.session.session_key
        product_id = request.data.get("product_id")
        action = request.data.get("action", "inc")

        if action == "inc":
            increment_quantity(session_id, product_id)
        else:
            decrement_quantity(session_id, product_id)

        return Response(status=status.HTTP_204_NO_CONTENT)
