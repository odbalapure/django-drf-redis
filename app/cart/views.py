from rest_framework.views import APIView
from .serializer import AddToCartSerializer
from .redis_cart import add_to_cart
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema


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
