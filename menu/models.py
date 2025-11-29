from django.db import models
from django.utils import timezone
import uuid


class Category(models.Model):
    """أقسام القائمة"""
    name = models.CharField('الاسم', max_length=100)
    icon = models.CharField('الأيقونة', max_length=50, default='bx-food-menu', 
                           help_text='اسم أيقونة Boxicons مثل: bx-coffee, bx-drink')
    image = models.ImageField('الصورة', upload_to='categories/', blank=True, null=True)
    order = models.PositiveIntegerField('الترتيب', default=0)
    is_active = models.BooleanField('نشط', default=True)
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)

    class Meta:
        verbose_name = 'قسم'
        verbose_name_plural = 'الأقسام'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    @property
    def items_count(self):
        return self.items.filter(is_available=True).count()


class MenuItem(models.Model):
    """عناصر القائمة"""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, 
                                 related_name='items', verbose_name='القسم')
    name = models.CharField('الاسم', max_length=200)
    description = models.TextField('الوصف', blank=True)
    price = models.DecimalField('السعر', max_digits=8, decimal_places=2)
    image = models.ImageField('الصورة', upload_to='products/')
    is_available = models.BooleanField('متوفر', default=True)
    is_vegetarian = models.BooleanField('نباتي', default=False)
    is_spicy = models.BooleanField('حار', default=False)
    is_featured = models.BooleanField('مميز', default=False)
    order = models.PositiveIntegerField('الترتيب', default=0)
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('آخر تحديث', auto_now=True)

    class Meta:
        verbose_name = 'منتج'
        verbose_name_plural = 'المنتجات'
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"{self.name} - {self.price} درهم"


class Cart(models.Model):
    """سلة التسوق"""
    session_key = models.CharField('مفتاح الجلسة', max_length=100, unique=True)
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('آخر تحديث', auto_now=True)

    class Meta:
        verbose_name = 'سلة'
        verbose_name_plural = 'السلات'

    def __str__(self):
        return f"سلة {self.session_key[:8]}"

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def items_count(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    """عناصر السلة"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, 
                            related_name='items', verbose_name='السلة')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, 
                                  verbose_name='المنتج')
    quantity = models.PositiveIntegerField('الكمية', default=1)
    notes = models.TextField('ملاحظات', blank=True)

    class Meta:
        verbose_name = 'عنصر السلة'
        verbose_name_plural = 'عناصر السلة'
        unique_together = ['cart', 'menu_item']

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name}"

    @property
    def subtotal(self):
        return self.menu_item.price * self.quantity


class Order(models.Model):
    """الطلبات"""
    STATUS_CHOICES = [
        ('pending', 'قيد الانتظار'),
        ('confirmed', 'مؤكد'),
        ('preparing', 'قيد التحضير'),
        ('ready', 'جاهز'),
        ('delivered', 'تم التوصيل'),
        ('cancelled', 'ملغي'),
    ]

    DELIVERY_CHOICES = [
        ('pickup', 'استلام من المطعم'),
        ('delivery', 'توصيل'),
    ]

    order_number = models.CharField('رقم الطلب', max_length=20, unique=True, editable=False)
    customer_name = models.CharField('اسم العميل', max_length=100)
    customer_phone = models.CharField('رقم الهاتف', max_length=20)
    delivery_type = models.CharField('نوع التوصيل', max_length=20, 
                                     choices=DELIVERY_CHOICES, default='pickup')
    address = models.TextField('العنوان', blank=True)
    notes = models.TextField('ملاحظات', blank=True)
    total = models.DecimalField('المجموع', max_digits=10, decimal_places=2)
    status = models.CharField('الحالة', max_length=20, 
                             choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField('تاريخ الطلب', auto_now_add=True)
    updated_at = models.DateTimeField('آخر تحديث', auto_now=True)

    class Meta:
        verbose_name = 'طلب'
        verbose_name_plural = 'الطلبات'
        ordering = ['-created_at']

    def __str__(self):
        return f"طلب #{self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ORD-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    """عناصر الطلب"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, 
                             related_name='items', verbose_name='الطلب')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.SET_NULL, 
                                  null=True, verbose_name='المنتج')
    name = models.CharField('اسم المنتج', max_length=200)
    price = models.DecimalField('السعر', max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField('الكمية', default=1)
    notes = models.TextField('ملاحظات', blank=True)

    class Meta:
        verbose_name = 'عنصر الطلب'
        verbose_name_plural = 'عناصر الطلب'

    def __str__(self):
        return f"{self.quantity}x {self.name}"

    @property
    def subtotal(self):
        return self.price * self.quantity
