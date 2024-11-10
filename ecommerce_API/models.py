from django.db import models
from django.contrib.auth.models import User


class User(User):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('customer', 'Customer'),  # Added a customer role
    )
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')
    
    # Additional user information
    full_name = models.CharField(max_length=35, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


# Category model
class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    def __str__(self):
        return self.name

# Product model
class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  # Reference to Category model
    description = models.TextField()
    reference = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    margin = models.DecimalField(max_digits=10, decimal_places=2)
    tva = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    image = models.ImageField(upload_to='produit_images/')
    promo_video = models.FileField(upload_to='promo_videos/', null=True, blank=True)
    in_stock = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    promo = models.BooleanField(default=False)

    def __str__(self):
        return self.name

# Gallery model
class ProductGallery(models.Model):
    image = models.ImageField(upload_to='produit_images/')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="gallery_produits", default=None, null=True, blank=True)

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    dimension = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    variant_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} - {self.color} {self.dimension}"
# BuyingBill model
class BuyingBill(models.Model):
    bill_id = models.CharField(max_length=50, unique=True)
    date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50)  # Example: 'credit_card', 'cash', etc.
    is_paid = models.BooleanField(default=False)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    fournisseur = models.CharField(max_length=250)  # Assuming a Fournisseur model exists

    def __str__(self):
        return self.bill_id

# ProductInBill model
class ProductInBill(models.Model):
    bill = models.ForeignKey(BuyingBill, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

# Order model
class Order(models.Model):
    STATUS_CHOICES = [
        ('En attente', 'En attente'),
        ('En traitement', 'En traitement'),
        ('Expédié', 'Expédié'),
        ('Livré', 'Livré'),
        ('Annulé', 'Annulé'),
    ]

    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )  # Links order to a registered user, or null for guest checkout
    customer_fullname = models.CharField(max_length=255, blank=True)  # For guest users
    customer_phonenumber = models.CharField(max_length=255, blank=True)  # For guest users
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='En attente')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.CharField(max_length=255)
    billing_address = models.CharField(max_length=255)
    payment_status = models.BooleanField(default=False)  # True if payment is completed

    def __str__(self):
        return f"Order {self.id} by {self.user if self.user else self.customer_fullname or 'Guest'}"

# ProductInOrder model
class ProductInOrder(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

# Cart model
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Cart for {self.user.username}"

# CartItem model
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} in {self.cart}"

# ReturnBill model
class ReturnBill(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    bill_id = models.CharField(max_length=50, unique=True)
    return_reason = models.TextField()
    refunded = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


########################### Marketing & Content management system Models #####################################################
# HomeCarouselSection model
class HomeCarouselSection(models.Model):
    image_desktop = models.ImageField(upload_to='carousel_images/')
    image_phone = models.ImageField(upload_to='carousel_images/')
    text = models.CharField(max_length=255)
    link = models.URLField()
    header = models.CharField(max_length=255)
    show = models.BooleanField(default=True)

# FAQ model
class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    show = models.BooleanField(default=True)

# Newsletter model
class Newsletter(models.Model):
    email = models.EmailField(unique=True)

# Promotion model
class Promotion(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    carousel_image = models.ImageField(upload_to='promotion_images/')
    text = models.CharField(max_length=255)
    taux_promo = models.DecimalField(max_digits=5, decimal_places=2)
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()

    def __str__(self):
        return f"Promotion for {self.product.name}"
