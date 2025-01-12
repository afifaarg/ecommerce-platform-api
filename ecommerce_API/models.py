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

class Fournisseur(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    def __str__(self):
        return self.name
    
class Client(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    def __str__(self):
        return self.name
    
# BuyingBill model
class BuyingBill(models.Model):
    bill_id = models.CharField(max_length=50, unique=True)
    date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50, null=True, blank=True, default="") 
    is_paid = models.BooleanField(default=False)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.CASCADE, null=True, blank=True, default=None)

    def __str__(self):
        return self.bill_id

# ProductInBill model
class ProductInBill(models.Model):
    bill = models.ForeignKey(BuyingBill, on_delete=models.CASCADE, related_name="products")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

# Order model
class Order(models.Model):
    STATUS_CHOICES = [
        ('En attente', 'En attente'),   
        ('Confirmé', 'Confirmé'),
        ('Annulé', 'Annulé'),
    ]

    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )  # Links order to a registered user, or null for guest checkout
    client = models.ForeignKey(
        Client, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        default=None
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
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default="0.00")
    total_price = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True, default="0.00")

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



########################### Marketing & Content management system Models #####################################################
# HomeCarouselSection model
class Contact(models.Model):
    STATUT_CHOICES = [
        ('ferme', 'Fermé'),
        ('ouvert', 'Ouvert'),
    ]

    nom = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    etat = models.CharField(max_length=6, choices=STATUT_CHOICES, default='ouvert')

    def __str__(self):
        return f"{self.nom} - {self.etat}"
    
class HomeCarouselSection(models.Model):
    file = models.FileField(
        upload_to='carousel_files/', 
        help_text="Upload an image or video.",
        default=""
    )
    title = models.CharField(max_length=25, blank=True, null=True, default="")
    show = models.BooleanField(default=True)
    dateAjout = models.DateTimeField( auto_now=True)

    def __str__(self):
        return self.header

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
