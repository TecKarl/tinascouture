from .cart import Cart


def cart(request):
    """Makes the cart available in every template (for the header badge)."""
    return {"cart": Cart(request)}
