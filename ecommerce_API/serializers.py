from rest_framework import serializers
from .models import Newsletter, ProductGallery, Product, Category

class NewsletterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Newsletter
        fields = ['email']  
        
class ProductGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductGallery
        fields = ['image']
        
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name']

class ProductSerializer(serializers.ModelSerializer):
    gallery_images = serializers.SerializerMethodField()  # For the gallery images
    category = serializers.SerializerMethodField()        # For the category name
    image = serializers.SerializerMethodField()           # For the main image URL

    class Meta:
        model = Product
        fields = [
            'id', 
            'name', 
            'category', 
            'description', 
            'reference', 
            'price', 
            'cost_price', 
            'margin', 
            'image',           # Return the main image URL
            'tva', 
            'in_stock', 
            'is_active', 
            'created_at', 
            'promo', 
            'gallery_images',  # Include the gallery images in the serialized output
        ]
    
    def get_category(self, obj):
        """Return the category name instead of its ID."""
        return obj.category.name

    def get_image(self, obj):
        """Return the full URL for the product image."""
        if obj.image:
            return 'http://127.0.0.1:8000' + obj.image.url
        return None

    def get_gallery_images(self, obj):
        """Return the full URLs of the gallery images."""
        return ['http://127.0.0.1:8000' + gallery.image.url for gallery in obj.gallery_produits.all()]