from django.contrib import admin
from .models import (
    User,
    Category,
    Product,
    ProductGallery,
    BuyingBill,
    ProductInBill,
    Order,
    ProductInOrder,
    Cart,
    CartItem,
    ReturnBill,
    HomeCarouselSection,
    FAQ,
    Newsletter,
    Promotion
)

# Customizing the admin for the User model
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'phone_number', 'created_at', 'updated_at')
    search_fields = ('username', 'email')
    list_filter = ('role',)

# Customizing the admin for the Category model
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

# Customizing the admin for the Product model
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'cost_price', 'is_active', 'created_at')
    search_fields = ('name', 'reference')
    list_filter = ('category', 'is_active', 'promo')

# Customizing the admin for the ProductGallery model
@admin.register(ProductGallery)
class ProductGalleryAdmin(admin.ModelAdmin):
    list_display = ('product', 'image')
    search_fields = ('product__name',)

# Customizing the admin for the BuyingBill model
@admin.register(BuyingBill)
class BuyingBillAdmin(admin.ModelAdmin):
    list_display = ('bill_id', 'date', 'payment_method', 'is_paid', 'total_amount')
    search_fields = ('bill_id',)

# Customizing the admin for the ProductInBill model
@admin.register(ProductInBill)
class ProductInBillAdmin(admin.ModelAdmin):
    list_display = ('bill', 'product', 'quantity', 'total_price')
    search_fields = ('bill__bill_id', 'product__name')

# Customizing the admin for the Order model
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'order_status', 'created_at')
    search_fields = ('user__username',)

# Customizing the admin for the ProductInOrder model
@admin.register(ProductInOrder)
class ProductInOrderAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'total_price')
    search_fields = ('order__user__username', 'product__name')

# Customizing the admin for the Cart model
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at', 'is_active')
    search_fields = ('user__username',)

# Customizing the admin for the CartItem model
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity')
    search_fields = ('cart__user__username', 'product__name')

# Customizing the admin for the ReturnBill model
@admin.register(ReturnBill)
class ReturnBillAdmin(admin.ModelAdmin):
    list_display = ('order', 'bill_id', 'return_reason', 'refunded', 'created_at')
    search_fields = ('bill_id',)

# Customizing the admin for the HomeCarouselSection model
@admin.register(HomeCarouselSection)
class HomeCarouselSectionAdmin(admin.ModelAdmin):
    list_display = ('header', 'text', 'show')
    search_fields = ('header',)

# Customizing the admin for the FAQ model
@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'show')
    search_fields = ('question',)

# Customizing the admin for the Newsletter model
@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('email',)
    search_fields = ('email',)

# Customizing the admin for the Promotion model
@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('product', 'text', 'taux_promo', 'date_start', 'date_end')
    search_fields = ('product__name', 'text')
