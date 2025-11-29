from django.urls import path
from . import views

urlpatterns = [
    # الصفحات
    path('', views.menu_view, name='menu'),
    path('about/', views.about_view, name='about'),
    path('checkout/', views.checkout_view, name='checkout'),
    
    # API السلة
    path('api/cart/add/', views.cart_add, name='cart_add'),
    path('api/cart/update/', views.cart_update, name='cart_update'),
    path('api/cart/remove/', views.cart_remove, name='cart_remove'),
    path('api/cart/content/', views.cart_content, name='cart_content'),
    path('api/cart/clear/', views.cart_clear, name='cart_clear'),
    
    # الطلبات
    path('api/order/create/', views.create_order, name='create_order'),
    path('order/whatsapp/<int:item_id>/', views.order_whatsapp, name='order_whatsapp'),
]
