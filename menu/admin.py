from django.contrib import admin
from django.utils.html import format_html
from .models import Category, MenuItem, Cart, CartItem, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon_preview', 'order', 'items_count', 'is_active']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    ordering = ['order']

    def icon_preview(self, obj):
        return format_html('<i class="bx {}"></i> {}', obj.icon, obj.icon)
    icon_preview.short_description = 'الأيقونة'


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['image_preview', 'name', 'category', 'price_display', 
                    'is_available', 'is_featured', 'order']
    list_editable = ['is_available', 'is_featured', 'order']
    list_filter = ['category', 'is_available', 'is_vegetarian', 'is_spicy', 'is_featured']
    search_fields = ['name', 'description']
    list_per_page = 20
    ordering = ['category', 'order']

    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('category', 'name', 'description', 'price', 'image')
        }),
        ('الخصائص', {
            'fields': ('is_available', 'is_vegetarian', 'is_spicy', 'is_featured', 'order')
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:50px;height:50px;object-fit:cover;border-radius:8px;">',
                obj.image.url
            )
        return "—"
    image_preview.short_description = 'الصورة'

    def price_display(self, obj):
        return format_html('<strong>{} درهم</strong>', obj.price)
    price_display.short_description = 'السعر'

    actions = ['make_available', 'make_unavailable']

    @admin.action(description='تحديد كـ متوفر')
    def make_available(self, request, queryset):
        queryset.update(is_available=True)

    @admin.action(description='تحديد كـ غير متوفر')
    def make_unavailable(self, request, queryset):
        queryset.update(is_available=False)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['name', 'price', 'quantity', 'subtotal']

    def subtotal(self, obj):
        return f"{obj.subtotal} درهم"
    subtotal.short_description = 'المجموع الفرعي'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer_name', 'customer_phone', 
                    'total_display', 'status', 'delivery_type', 'created_at']
    list_filter = ['status', 'delivery_type', 'created_at']
    search_fields = ['order_number', 'customer_name', 'customer_phone']
    readonly_fields = ['order_number', 'total', 'created_at', 'updated_at']
    list_per_page = 20
    date_hierarchy = 'created_at'
    inlines = [OrderItemInline]

    fieldsets = (
        ('معلومات الطلب', {
            'fields': ('order_number', 'status', 'total')
        }),
        ('معلومات العميل', {
            'fields': ('customer_name', 'customer_phone', 'delivery_type', 'address')
        }),
        ('ملاحظات', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('التواريخ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def total_display(self, obj):
        return format_html('<strong style="color:#556B2F;">{} درهم</strong>', obj.total)
    total_display.short_description = 'المجموع'


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['session_key', 'items_count', 'total', 'created_at']
    readonly_fields = ['session_key', 'created_at', 'updated_at']
    inlines = [CartItemInline]
