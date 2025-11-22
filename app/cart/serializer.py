from rest_framework import serializers


class CartItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    name = serializers.CharField()
    price = serializers.FloatField()
    quantity = serializers.IntegerField(min_value=1, default=1)


class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    name = serializers.CharField()
    price = serializers.FloatField()
    quantity = serializers.IntegerField(min_value=1, default=1)


class RemoveFromCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
