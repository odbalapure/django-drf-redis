from django.conf import settings
import json


r = settings.REDIS_CLIENT


def _cart_key(session_id):
    return f"cart:{session_id}"


def get_cart(session_id):
    key = _cart_key(session_id)
    raw_cart = r.hgetall(key)
    return [json.loads(item) for item in raw_cart.values()]

    # def ensure_str(v):
    #     return v if isinstance(v, str) else v.decode("utf-8")

    # return [json.loads(ensure_str(item)) for item in raw_cart.values()]


def remove_from_cart(session_id, product_id):
    key = _cart_key(session_id)
    r.hdel(key, product_id)

    if r.hlen(key) == 0:
        promo_key = f"cart:{session_id}:promo_code"
        r.delete(promo_key)


def clear_cart(session_id):
    key = _cart_key(session_id)
    r.delete(key)


def add_to_cart(session_id, product_id, quantity, name, price):
    cart_key = _cart_key(session_id)

    product_data = {
        "product_id": product_id,
        "name": name,
        "price": price,
        "quantity": quantity,
    }

    r.hset(cart_key, product_id, json.dumps(product_data))


def increment_quantity(session_id, product_id, step=1):
    key = _cart_key(session_id)
    existing = r.hget(key, product_id)

    if not existing:
        return False

    data = json.loads(existing)
    data["quantity"] += step
    r.hset(key, product_id, json.dumps(data))

    return True


def decrement_quantity(session_id, product_id, step=1):
    key = _cart_key(session_id)
    existing = r.hget(key, product_id)

    if not existing:
        return False

    data = json.loads(existing)
    data["quantity"] -= max(data["quantity"] - step, 1)
    r.hset(key, product_id, json.dumps(data))

    return True


def set_quantity(session_id, product_id, quantity):
    key = _cart_key(session_id)
    existing = r.hget(key, product_id)

    if not existing:
        return False

    data = json.loads(existing)
    data["quantity"] = quantity
    r.hset(key, product_id, json.dumps(data))

    return True


def set_cart_promo_code(session_id, promo_code):
    key = f"cart:{session_id}:promo_code"
    r.set(key, promo_code)


def get_cart_promo_code(session_id):
    key = f"cart:{session_id}:promo_code"
    return r.get(key)


def update_cart_item(session_id, product_id, name, price, quantity):
    key = _cart_key(session_id)

    product_data = {
        "product_id": product_id,
        "name": name,
        "quantity": quantity,
        "price": float(price),
    }

    r.hset(key, product_id, json.dumps(product_data))
