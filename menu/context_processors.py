from django.conf import settings
from .models import Cart


def cart_context(request):
    """إضافة معلومات السلة لكل الصفحات"""
    cart_count = 0
    cart_total = 0
    cart_items = []
    
    if request.session.session_key:
        try:
            cart = Cart.objects.get(session_key=request.session.session_key)
            cart_count = cart.items_count
            cart_total = cart.total
            cart_items = cart.items.select_related('menu_item').all()
        except Cart.DoesNotExist:
            pass
    
    return {
        'cart_count': cart_count,
        'cart_total': cart_total,
        'cart_items': cart_items,
    }


def restaurant_info(request):
    """معلومات المطعم لكل الصفحات"""
    return {
        'restaurant': {
            'name': settings.RESTAURANT_NAME,
            'phone': settings.RESTAURANT_PHONE,
            'whatsapp': settings.RESTAURANT_WHATSAPP,
            'address': settings.RESTAURANT_ADDRESS,
            'maps': settings.RESTAURANT_MAPS,
        }
    }
