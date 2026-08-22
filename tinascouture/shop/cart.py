from decimal import Decimal

from .models import Apparel, Perfume

CART_SESSION_ID = "cart"

MODEL_MAP = {
    "apparel": Apparel,
    "perfume": Perfume,
}


def get_product_model(product_type):
    """Look up the model class for a cart item type ('apparel' / 'perfume')."""
    model = MODEL_MAP.get(product_type)
    if model is None:
        raise ValueError(f"Unknown product type: {product_type}")
    return model


class Cart:
    """A simple session-backed shopping cart that holds both product types.

    Apparel keys include the selected size, while perfume keys do not.
    """

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_ID)
        if not cart:
            cart = self.session[CART_SESSION_ID] = {}
        self.cart = cart

    @staticmethod
    def _key(product_type, product_id, size=""):
        return f"{product_type}:{product_id}:{size}" if product_type == "apparel" else f"{product_type}:{product_id}"

    def save(self):
        self.session.modified = True

    def add(self, product, product_type, quantity=1, override_quantity=False, size=""):
        """Add a product, or change its quantity by `quantity`.

        If override_quantity is True, quantity becomes the new quantity.
        Otherwise quantity is added to (or subtracted from) the current amount.
        The result is always clamped between 0 and the product's live stock.
        """
        key = self._key(product_type, product.id, size)
        if key not in self.cart:
            self.cart[key] = {
                "quantity": 0,
                "price": str(product.price),
                "type": product_type,
                "size": size,
            }

        if override_quantity:
            new_quantity = quantity
        else:
            new_quantity = self.cart[key]["quantity"] + quantity

        new_quantity = max(0, min(new_quantity, product.stock))

        if new_quantity == 0:
            self.remove(product, product_type, size)
        else:
            self.cart[key]["quantity"] = new_quantity
            self.cart[key]["price"] = str(product.price)
            self.save()

    def remove(self, product, product_type, size=""):
        key = self._key(product_type, product.id, size)
        if key in self.cart:
            del self.cart[key]
            self.save()

    def clear(self):
        self.session[CART_SESSION_ID] = {}
        self.save()

    def __iter__(self):
        # Batch-fetch each product type to avoid N+1 queries.
        ids_by_type = {"apparel": [], "perfume": []}
        for key, item in self.cart.items():
            ids_by_type[item["type"]].append(key.split(":", 2)[1])

        products_map = {}
        for product_type, ids in ids_by_type.items():
            if not ids:
                continue
            model = get_product_model(product_type)
            for obj in model.objects.filter(id__in=ids):
                products_map[f"{product_type}:{obj.id}"] = obj

        for key, item in self.cart.items():
            product = products_map.get(f"{item['type']}:{key.split(':', 2)[1]}")
            if not product:
                continue
            price = Decimal(item["price"])
            quantity = item["quantity"]
            yield {
                "product": product,
                "product_type": item["type"],
                "quantity": quantity,
                "price": price,
                "total_price": price * quantity,
                "size": item.get("size", ""),
            }

    def __len__(self):
        return sum(item["quantity"] for item in self.cart.values())

    def get_total_price(self):
        return sum(
            Decimal(item["price"]) * item["quantity"] for item in self.cart.values()
        )
