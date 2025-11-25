from rest_framework.views import APIView
from .serializer import (
    AddToCartSerializer,
    CartItemSerializer,
    RemoveFromCartSerializer,
    UpdateQuantitySerializer,
    SetQuantitySerializer,
    CartPromoSerializer,
    CheckoutResponseItemSerializer,
)
from .redis_cart import (
    add_to_cart,
    get_cart,
    remove_from_cart,
    clear_cart,
    increment_quantity,
    decrement_quantity,
    set_quantity,
    set_cart_promo_code,
    get_cart_promo_code,
    update_cart_item,
)
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from inventory.models import Product


# Get, clear cart
class CartView(APIView):
    @extend_schema(
        responses={200: CartItemSerializer(many=True)}, description="Get cart products"
    )
    def get(self, request):
        session_id = request.session.session_key
        cart_data = get_cart(session_id)
        promo_code = get_cart_promo_code(session_id)

        return Response(
            {"items": cart_data, "promo_code": promo_code}, status=status.HTTP_200_OK
        )

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


# Set cart quantity
class SetQuantityView(APIView):
    @extend_schema(
        request=SetQuantitySerializer,
        responses={200: None},
        description="Set product quantity",
    )
    def post(self, request):
        session_id = request.session.session_key

        serializer = SetQuantitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data["product_id"]
        quantity = serializer.validated_data["quantity"]

        updated = set_quantity(session_id, product_id, quantity)
        if not updated:
            return Response({"error": "Product not found in cart."}, status=404)

        return Response(
            {"message": f"Product quantity updated to {quantity}."}, status=200
        )


# Set promo code for cart
class CartPromoView(APIView):
    @extend_schema(
        request=CartPromoSerializer,
        responses={200: None},
        description="Set product quantity",
    )
    def post(self, request):
        session_id = request.session.session_key

        serializer = CartPromoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        promo_code = serializer.validated_data["promo_code"]
        set_cart_promo_code(session_id, promo_code)

        return Response({"message": "Promo code applied"}, status=200)


class CheckoutPromoView(APIView):
    @extend_schema(
        responses={200: CheckoutResponseItemSerializer(many=True)},
        description="Valid and sanitize cart before checkout. Remove missing products, update price/name if needed.",
    )
    def post(self, request):
        session_id = request.session.session_key
        cart_items = get_cart(session_id)

        if not cart_items:
            return Response([], status=status.HTTP_200_OK)

        product_ids = [item["product_id"] for item in cart_items]
        products = Product.objects.filter(id__in=product_ids, is_active=True)

        product_map = {product.id: product for product in products}

        cleaned_cart = []

        for item in cart_items:
            product_id = item["product_id"]
            product = product_map.get(product_id)

            if not product:
                remove_from_cart(session_id, product_id)
                continue

            # Check if Redis-stored name/price differs
            if item["name"] != product.name or float(item["price"]) != float(
                product.price
            ):
                update_cart_item(
                    session_id,
                    product_id,
                    product.name,
                    product.price,
                    item["quantity"],
                )
                item["name"] = product.name
                item["price"] = float(product.price)

            item["valid"] = True
            item["error"] = ""
            cleaned_cart.append(item)

        return Response(cleaned_cart, status=status.HTTP_200_OK)
