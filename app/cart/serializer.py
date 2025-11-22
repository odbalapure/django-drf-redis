from rest_framework import serializers


class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    name = serializers.CharField()
    price = serializers.FloatField()
    quantity = serializers.IntegerField(min_value=1, default=1)
