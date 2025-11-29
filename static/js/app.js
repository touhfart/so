/**
 * So Bnin - Restaurant Menu App
 * Main JavaScript File
 */

// ============ Utilities ============
const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => document.querySelectorAll(selector);

// API Helper
async function api(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': CSRF_TOKEN,
        },
    };
    
    const response = await fetch(url, { ...defaultOptions, ...options });
    return response.json();
}

// ============ Toast Notifications ============
function showToast(message, duration = 2500) {
    const toast = $('#toast');
    const toastMessage = $('#toast-message');
    
    toastMessage.textContent = message;
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, duration);
}

// ============ Cart Functions ============
const Cart = {
    // تحديث عداد السلة
    updateCount(count) {
        const cartCount = $('#cart-count');
        if (cartCount) {
            cartCount.textContent = count;
            cartCount.dataset.count = count;
        }
    },
    
    // إضافة للسلة
    async add(itemId, quantity = 1) {
        try {
            const result = await api('/api/cart/add/', {
                method: 'POST',
                body: JSON.stringify({ item_id: itemId, quantity }),
            });
            
            if (result.success) {
                this.updateCount(result.cart_count);
                showToast(result.message);
                this.showQuantityControls(itemId, quantity);
            }
            
            return result;
        } catch (error) {
            console.error('Error adding to cart:', error);
            showToast('حدث خطأ');
        }
    },
    
    // تحديث الكمية
    async update(itemId, quantity) {
        try {
            const result = await api('/api/cart/update/', {
                method: 'POST',
                body: JSON.stringify({ item_id: itemId, quantity }),
            });
            
            if (result.success) {
                this.updateCount(result.cart_count);
                
                if (quantity <= 0) {
                    this.hideQuantityControls(itemId);
                } else {
                    this.updateQuantityDisplay(itemId, quantity);
                }
                
                // تحديث محتوى السلة في المودال
                this.refreshModalContent();
            }
            
            return result;
        } catch (error) {
            console.error('Error updating cart:', error);
        }
    },
    
    // حذف من السلة
    async remove(itemId) {
        try {
            const result = await api('/api/cart/remove/', {
                method: 'POST',
                body: JSON.stringify({ item_id: itemId }),
            });
            
            if (result.success) {
                this.updateCount(result.cart_count);
                this.hideQuantityControls(itemId);
                this.refreshModalContent();
            }
            
            return result;
        } catch (error) {
            console.error('Error removing from cart:', error);
        }
    },
    
    // تفريغ السلة
    async clear() {
        try {
            const result = await api('/api/cart/clear/', {
                method: 'POST',
            });
            
            if (result.success) {
                this.updateCount(0);
                this.refreshModalContent();
                // إخفاء كل أزرار الكمية
                $$('.card__quantity').forEach(el => el.classList.add('hidden'));
                $$('.card__actions').forEach(el => el.classList.remove('hidden'));
            }
            
            return result;
        } catch (error) {
            console.error('Error clearing cart:', error);
        }
    },
    
    // تحديث محتوى المودال
    async refreshModalContent() {
        try {
            const result = await api('/api/cart/content/');
            const cartContent = $('#cart-content');
            if (cartContent && result.html) {
                cartContent.innerHTML = result.html;
                this.bindModalEvents();
            }
        } catch (error) {
            console.error('Error refreshing cart:', error);
        }
    },
    
    // إظهار أزرار الكمية
    showQuantityControls(itemId, quantity) {
        const card = $(`.card[data-id="${itemId}"]`);
        if (!card) return;
        
        const actions = card.querySelector('.card__actions');
        const qtyControls = card.querySelector('.card__quantity');
        const qtyValue = card.querySelector('.qty-value');
        
        if (actions) actions.classList.add('hidden');
        if (qtyControls) qtyControls.classList.remove('hidden');
        if (qtyValue) qtyValue.textContent = quantity;
    },
    
    // إخفاء أزرار الكمية
    hideQuantityControls(itemId) {
        const card = $(`.card[data-id="${itemId}"]`);
        if (!card) return;
        
        const actions = card.querySelector('.card__actions');
        const qtyControls = card.querySelector('.card__quantity');
        
        if (actions) actions.classList.remove('hidden');
        if (qtyControls) qtyControls.classList.add('hidden');
    },
    
    // تحديث عرض الكمية
    updateQuantityDisplay(itemId, quantity) {
        const qtyValue = $(`#qty-value-${itemId}`);
        if (qtyValue) qtyValue.textContent = quantity;
    },
    
    // ربط أحداث المودال
    bindModalEvents() {
        // أزرار الكمية في المودال
        $('#cart-content')?.querySelectorAll('.qty-btn--plus').forEach(btn => {
            btn.onclick = () => {
                const itemId = btn.dataset.id;
                const qtyEl = btn.parentElement.querySelector('.qty-value');
                const newQty = parseInt(qtyEl.textContent) + 1;
                this.update(itemId, newQty);
            };
        });
        
        $('#cart-content')?.querySelectorAll('.qty-btn--minus').forEach(btn => {
            btn.onclick = () => {
                const itemId = btn.dataset.id;
                const qtyEl = btn.parentElement.querySelector('.qty-value');
                const newQty = parseInt(qtyEl.textContent) - 1;
                this.update(itemId, newQty);
            };
        });
        
        // زر الحذف
        $('#cart-content')?.querySelectorAll('.cart-item__remove').forEach(btn => {
            btn.onclick = () => this.remove(btn.dataset.id);
        });
        
        // زر تفريغ السلة
        $('#clear-cart')?.addEventListener('click', () => {
            if (confirm('هل تريد تفريغ السلة؟')) {
                this.clear();
            }
        });
    }
};

// ============ Modal Functions ============
const Modal = {
    element: null,
    
    init() {
        this.element = $('#cart-modal');
        
        // فتح المودال
        $('#cart-fab')?.addEventListener('click', () => this.open());
        
        // إغلاق المودال
        $('#modal-close')?.addEventListener('click', () => this.close());
        $('#modal-backdrop')?.addEventListener('click', () => this.close());
        
        // إغلاق بـ Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen()) {
                this.close();
            }
        });
    },
    
    open() {
        Cart.refreshModalContent();
        this.element?.classList.add('active');
        document.body.style.overflow = 'hidden';
    },
    
    close() {
        this.element?.classList.remove('active');
        document.body.style.overflow = '';
    },
    
    isOpen() {
        return this.element?.classList.contains('active');
    }
};

// ============ Scroll Functions ============
const ScrollManager = {
    init() {
        const scrollBtn = $('#scroll-top');
        
        window.addEventListener('scroll', () => {
            if (window.scrollY > 300) {
                scrollBtn?.classList.add('visible');
            } else {
                scrollBtn?.classList.remove('visible');
            }
        });
        
        scrollBtn?.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }
};

// ============ Initialize ============
document.addEventListener('DOMContentLoaded', () => {
    // تهيئة المكونات
    Modal.init();
    ScrollManager.init();
    Cart.bindModalEvents();
    
    // أزرار إضافة للسلة
    $$('.card__btn--cart').forEach(btn => {
        btn.addEventListener('click', () => {
            const itemId = btn.dataset.id;
            Cart.add(itemId);
        });
    });
    
    // أزرار + في الكروت
    $$('.card .qty-btn--plus').forEach(btn => {
        btn.addEventListener('click', () => {
            const itemId = btn.dataset.id;
            const qtyEl = $(`#qty-value-${itemId}`);
            const newQty = parseInt(qtyEl.textContent) + 1;
            Cart.update(itemId, newQty);
            qtyEl.textContent = newQty;
        });
    });
    
    // أزرار - في الكروت
    $$('.card .qty-btn--minus').forEach(btn => {
        btn.addEventListener('click', () => {
            const itemId = btn.dataset.id;
            const qtyEl = $(`#qty-value-${itemId}`);
            const currentQty = parseInt(qtyEl.textContent);
            const newQty = currentQty - 1;
            
            if (newQty <= 0) {
                Cart.update(itemId, 0);
            } else {
                Cart.update(itemId, newQty);
                qtyEl.textContent = newQty;
            }
        });
    });

    // تأثير الظل على شريط الأقسام
    const categoriesNav = $('.categories');
    const categoriesContainer = $('.categories__container');

    if (categoriesNav && categoriesContainer) {
        function updateCategoriesShadow() {
            const { scrollLeft, scrollWidth, clientWidth } = categoriesContainer;

            // إظهار ظل اليمين إذا كان هناك المزيد
            if (scrollWidth > clientWidth && scrollLeft < scrollWidth - clientWidth - 5) {
                categoriesNav.classList.add('show-right');
            } else {
                categoriesNav.classList.remove('show-right');
            }

            // إظهار ظل اليسار إذا تم التمرير
            if (scrollLeft > 5) {
                categoriesNav.classList.add('show-left');
            } else {
                categoriesNav.classList.remove('show-left');
            }
        }

        // تشغيل عند التحميل والتمرير
        updateCategoriesShadow();
        categoriesContainer.addEventListener('scroll', updateCategoriesShadow);
        window.addEventListener('resize', updateCategoriesShadow);
    }
});