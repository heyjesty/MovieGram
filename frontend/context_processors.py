from backend.models import Category


def store(request):
    """Navigation data shared by every page."""
    cart_count = 0
    if request.user.is_authenticated:
        cart_count = request.user.cart_items.count()
    return {
        "nav_categories": Category.objects.all(),
        "cart_count": cart_count,
    }
