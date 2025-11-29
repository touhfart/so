from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.conf import settings
from urllib.parse import quote
import json

from .models import Category, MenuItem, Cart, CartItem, Order, OrderItem


def get_or_create_cart(request):
    """الحصول على السلة أو إنشاء واحدة جديدة"""
    if not request.session.session_key:
        request.session.create()
    
    session_key = request.session.session_key
    cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart


def menu_view(request):
    """صفحة القائمة الرئيسية"""
    categories = Category.objects.filter(is_active=True).prefetch_related('items')
    items = MenuItem.objects.filter(is_available=True).select_related('category')
    
    # تصفية حسب القسم
    category_id = request.GET.get('category')
    if category_id:
        items = items.filter(category_id=category_id)
    
    # البحث
    search = request.GET.get('search', '').strip()
    if search:
        items = items.filter(name__icontains=search)
    
    context = {
        'categories': categories,
        'items': items,
        'selected_category': category_id,
        'search_query': search,
    }
    return render(request, 'menu.html', context)


def about_view(request):
    """صفحة من نحن"""
    return render(request, 'about.html')


# ============ API للسلة ============

@require_POST
def cart_add(request):
    """إضافة منتج للسلة"""
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        quantity = int(data.get('quantity', 1))
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'success': False, 'error': 'بيانات غير صحيحة'}, status=400)
    
    menu_item = get_object_or_404(MenuItem, id=item_id, is_available=True)
    cart = get_or_create_cart(request)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        menu_item=menu_item,
        defaults={'quantity': quantity}
    )
    
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    
    return JsonResponse({
        'success': True,
        'message': f'تم إضافة {menu_item.name}',
        'cart_count': cart.items_count,
        'cart_total': float(cart.total),
    })


@require_POST
def cart_update(request):
    """تحديث كمية منتج في السلة"""
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        quantity = int(data.get('quantity', 1))
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'success': False, 'error': 'بيانات غير صحيحة'}, status=400)
    
    cart = get_or_create_cart(request)
    
    try:
        cart_item = CartItem.objects.get(cart=cart, menu_item_id=item_id)
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
    except CartItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'المنتج غير موجود في السلة'}, status=404)
    
    return JsonResponse({
        'success': True,
        'cart_count': cart.items_count,
        'cart_total': float(cart.total),
    })


@require_POST
def cart_remove(request):
    """حذف منتج من السلة"""
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'بيانات غير صحيحة'}, status=400)
    
    cart = get_or_create_cart(request)
    CartItem.objects.filter(cart=cart, menu_item_id=item_id).delete()
    
    return JsonResponse({
        'success': True,
        'cart_count': cart.items_count,
        'cart_total': float(cart.total),
    })


def cart_content(request):
    """محتوى السلة (للـ Modal)"""
    cart = get_or_create_cart(request)
    html = render_to_string('partials/_cart_content.html', {'cart': cart}, request)
    return JsonResponse({
        'html': html,
        'cart_count': cart.items_count,
        'cart_total': float(cart.total),
    })


@require_POST
def cart_clear(request):
    """تفريغ السلة"""
    cart = get_or_create_cart(request)
    cart.items.all().delete()
    return JsonResponse({'success': True, 'cart_count': 0, 'cart_total': 0})


# ============ الطلبات ============

def checkout_view(request):
    """صفحة إتمام الطلب"""
    cart = get_or_create_cart(request)
    if cart.items_count == 0:
        return redirect('menu')
    return render(request, 'checkout.html', {'cart': cart})


@require_POST
def create_order(request):
    """إنشاء طلب جديد"""
    cart = get_or_create_cart(request)
    
    if cart.items_count == 0:
        return JsonResponse({'success': False, 'error': 'السلة فارغة'}, status=400)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'بيانات غير صحيحة'}, status=400)
    
    # إنشاء الطلب
    order = Order.objects.create(
        customer_name=data.get('name', ''),
        customer_phone=data.get('phone', ''),
        delivery_type=data.get('delivery_type', 'pickup'),
        address=data.get('address', ''),
        notes=data.get('notes', ''),
        total=cart.total,
    )
    
    # نقل عناصر السلة للطلب
    for cart_item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            menu_item=cart_item.menu_item,
            name=cart_item.menu_item.name,
            price=cart_item.menu_item.price,
            quantity=cart_item.quantity,
            notes=cart_item.notes,
        )
    
    # تفريغ السلة
    cart.items.all().delete()
    
    # إنشاء رسالة واتساب
    whatsapp_message = generate_whatsapp_message(order)
    whatsapp_url = f"https://wa.me/{settings.RESTAURANT_WHATSAPP.replace('+', '')}?text={quote(whatsapp_message)}"
    
    return JsonResponse({
        'success': True,
        'order_number': order.order_number,
        'whatsapp_url': whatsapp_url,
    })


def generate_whatsapp_message(order):
    """إنشاء رسالة واتساب للطلب"""
    items_text = "\n".join([
        f"• {item.quantity}x {item.name} - {item.subtotal} درهم"
        for item in order.items.all()
    ])
    
    delivery_text = "استلام من المطعم" if order.delivery_type == 'pickup' else f"توصيل إلى: {order.address}"
    
    message = f"""🍽️ *طلب جديد #{order.order_number}*

👤 *العميل:* {order.customer_name}
📞 *الهاتف:* {order.customer_phone}
🚚 *التوصيل:* {delivery_text}

📝 *الطلب:*
{items_text}

💰 *المجموع:* {order.total} درهم
"""
    
    if order.notes:
        message += f"\n📌 *ملاحظات:* {order.notes}"
    
    return message


def order_whatsapp(request, item_id):
    """طلب منتج مباشرة عبر واتساب"""
    item = get_object_or_404(MenuItem, id=item_id, is_available=True)
    message = f"مرحباً، أريد طلب:\n\n• {item.name} - {item.price} درهم"
    whatsapp_url = f"https://wa.me/{settings.RESTAURANT_WHATSAPP.replace('+', '')}?text={quote(message)}"
    return redirect(whatsapp_url)
