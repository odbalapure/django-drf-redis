from django.conf import settings
import json


r = settings.REDIS_CLIENT

CART_TTL = 60 * 30  # 30 minutes


def _refresh_cart_ttl(session_id):
    r.expire(_qty_key(session_id), CART_TTL)
    r.expire(_details_key(session_id), CART_TTL)
    r.expire(f"{_cart_key(session_id)}:promo_code", CART_TTL)


def _cart_key(session_id):
    return f"cart:{session_id}"


def _qty_key(session_id):
    return f"{_cart_key(session_id)}:qty"


def _details_key(session_id):
    return f"{_cart_key(session_id)}:details"


def get_cart(session_id):
    qtys = r.hgetall(_qty_key(session_id))
    details = r.hgetall(_details_key(session_id))

    cart_items = []
    for pid, qty in qtys.items():
        detail_json = details.get(pid)
        if not detail_json:
            continue

        data = json.loads(detail_json)
        data["quantity"] = int(qty)
        cart_items.append(data)

    return cart_items


def remove_from_cart(session_id, product_id):
    r.hdel(_qty_key(session_id), product_id)
    r.hdel(_details_key(session_id), product_id)

    if r.hlen(_qty_key(session_id)) == 0:
        r.delete(f"{_cart_key(session_id)}:promo_code")

    _refresh_cart_ttl(session_id)


def clear_cart(session_id):
    r.delete(_qty_key(session_id))
    r.delete(_details_key(session_id))
    r.delete(f"{_cart_key(session_id)}:promo_code")


def add_to_cart(session_id, product_id, quantity, name, price):
    qt_key = _qty_key(session_id)
    details_key = _details_key(session_id)

    r.hincrby(qt_key, product_id, quantity)

    if not r.hexists(details_key, product_id):
        product_data = {
            "product_id": product_id,
            "name": name,
            "price": price,
        }

        r.hset(details_key, product_id, json.dumps(product_data))

    _refresh_cart_ttl(session_id)


def increment_quantity(session_id, product_id, step=1):
    r.hincrby(_qty_key(session_id), product_id, step)
    _refresh_cart_ttl(session_id)
    return True


def decrement_quantity(session_id, product_id, step=1):
    qt_key = _qty_key(session_id)
    new_qty = r.hincrby(qt_key, product_id, -step)

    if new_qty < 1:
        r.hdel(qt_key, product_id)
        r.hdel(_details_key(session_id), product_id)

    _refresh_cart_ttl(session_id)

    return True


def set_quantity(session_id, product_id, quantity):
    r.hset(_qty_key(session_id), product_id, quantity)
    _refresh_cart_ttl(session_id)

    return True


def set_cart_promo_code(session_id, promo_code):
    key = f"cart:{session_id}:promo_code"
    r.set(key, promo_code)
    _refresh_cart_ttl(session_id)


def get_cart_promo_code(session_id):
    key = f"cart:{session_id}:promo_code"
    return r.get(key)


def update_cart_item(session_id, product_id, name, price, quantity):
    details = {
        "product_id": product_id,
        "name": name,
        "price": float(price),
    }

    r.hset(_details_key(session_id), product_id, json.dumps(details))
    r.hset(_qty_key(session_id), product_id, quantity)
    _refresh_cart_ttl(session_id)
