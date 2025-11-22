from django.conf import settings
import json


r = settings.REDIS_CLIENT


def _cart_key(session_id):
    return f"cart:{session_id}"


def add_to_cart(session_id, product_id, quantity, name, price):
    cart_key = _cart_key(session_id)

    product_data = {
        "product_id": product_id,
        "name": name,
        "price": price,
        "quantity": quantity,
    }

    r.hset(cart_key, product_id, json.dumps(product_data))
