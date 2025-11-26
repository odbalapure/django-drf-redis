# redis_cart.py
import json

from django.conf import settings

r = settings.REDIS_CLIENT

CART_TTL = 60 * 30  # 30 minutes


def _refresh_cart_ttl_pipe(pipe, session_id):
    pipe.expire(_qty_key(session_id), CART_TTL)
    pipe.expire(_details_key(session_id), CART_TTL)
    pipe.expire(f"{_cart_key(session_id)}:promo_code", CART_TTL)


def _cart_key(session_id):
    return f"cart:{session_id}"


def _qty_key(session_id):
    return f"{_cart_key(session_id)}:qty"


def _details_key(session_id):
    return f"{_cart_key(session_id)}:details"


def add_to_cart(session_id, product_id, quantity, name, price):
    qty_key = _qty_key(session_id)
    details_key = _details_key(session_id)

    pipe = r.pipeline()
    pipe.hincrby(qty_key, product_id, quantity)

    if not r.hexists(details_key, product_id):
        product_data = {
            "product_id": product_id,
            "name": name,
            "price": float(price),
        }
        pipe.hset(details_key, product_id, json.dumps(product_data))

    _refresh_cart_ttl_pipe(pipe, session_id)
    pipe.execute()


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
    qty_key = _qty_key(session_id)
    details_key = _details_key(session_id)
    promo_key = f"{_cart_key(session_id)}:promo_code"

    pipe = r.pipeline()
    pipe.hdel(qty_key, product_id)
    pipe.hdel(details_key, product_id)

    if r.hlen(qty_key) == 0:  # 1 left before deletion
        pipe.delete(promo_key)

    _refresh_cart_ttl_pipe(pipe, session_id)
    pipe.execute()


def clear_cart(session_id):
    pipe = r.pipeline()
    pipe.delete(_qty_key(session_id))
    pipe.delete(_details_key(session_id))
    pipe.delete(f"{_cart_key(session_id)}:promo_code")
    pipe.execute()


def increment_quantity(session_id, product_id, step=1):
    pipe = r.pipeline()
    pipe.hincrby(_qty_key(session_id), product_id, step)
    _refresh_cart_ttl_pipe(pipe, session_id)
    pipe.execute()
    return True


def decrement_quantity(session_id, product_id, step=1):
    qty_key = _qty_key(session_id)
    details_key = _details_key(session_id)

    MAX_ATTEMPTS = 5

    for attempt in range(MAX_ATTEMPTS):
        try:
            with r.pipeline() as pipe:
                pipe.watch(qty_key)

                # Use direct client method (not through pipe)
                current_qty = r.hget(qty_key, product_id)
                if current_qty is None:
                    pipe.unwatch()
                    return False

                current_qty = int(current_qty)
                new_qty = current_qty - step

                pipe.multi()

                if new_qty < 1:
                    pipe.hdel(qty_key, product_id)
                    pipe.hdel(details_key, product_id)
                else:
                    pipe.hset(qty_key, product_id, new_qty)

                _refresh_cart_ttl_pipe(pipe, session_id)
                pipe.execute()
                return True

        except r.WatchError:
            continue


# def decrement_quantity(session_id, product_id, step=1):
#     qty_key = _qty_key(session_id)
#     details_key = _details_key(session_id)

#     # First, decrement and get new quantity
#     new_qty = r.hincrby(qty_key, product_id, -step)

#     if new_qty < 1:
#         # Quantity too low, clean up
#         pipe = r.pipeline()
#         pipe.hdel(qty_key, product_id)
#         pipe.hdel(details_key, product_id)
#         _refresh_cart_ttl_pipe(pipe, session_id)
#         pipe.execute()
#     else:
#         # Just refresh TTL
#         pipe = r.pipeline()
#         _refresh_cart_ttl_pipe(session_id)
#         pipe.execute()

#     return True


def set_quantity(session_id, product_id, quantity):
    key = _cart_key(session_id)
    existing = r.hget(key, product_id)

    if not existing:
        return False  # Nothing to update

    data = json.loads(existing)
    data["quantity"] = quantity
    r.hset(key, product_id, json.dumps(data))

    pipe = r.pipeline()
    _refresh_cart_ttl_pipe(pipe, session_id)
    pipe.execute()

    return True


def set_cart_promo_code(session_id, promo_code):
    pipe = r.pipeline()
    pipe.set(f"{_cart_key(session_id)}:promo_code", promo_code)
    _refresh_cart_ttl_pipe(pipe, session_id)
    pipe.execute()


def get_cart_promo_code(session_id):
    key = f"cart:{session_id}:promo_code"
    return r.get(key)


def update_cart_item(session_id, product_id, name, price, quantity):
    pipe = r.pipeline()
    details = {
        "product_id": product_id,
        "name": name,
        "price": float(price),
    }

    pipe.hset(_details_key(session_id), product_id, json.dumps(details))
    pipe.hset(_qty_key(session_id), product_id, quantity)
    _refresh_cart_ttl_pipe(pipe, session_id)
    pipe.execute()
