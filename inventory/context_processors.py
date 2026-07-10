from django.db.models import F
from .models import Product


def low_stock_notification(request):
    if not request.user.is_authenticated:
        return {'low_stock_count': 0, 'low_stock_list': []}

    products = Product.objects.filter(
        stock__lte=F('low_stock_threshold')
    ).select_related('category').order_by('stock')[:5]

    return {
        'low_stock_count': len(products),
        'low_stock_list': products,
    }
