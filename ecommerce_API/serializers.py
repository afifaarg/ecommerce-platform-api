from rest_framework import serializers
from .models import Newsletter, ProductGallery, Product, Category, Order, ProductInOrder, User

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
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None

    def get_gallery_images(self, obj):
        """Return the full URLs of the gallery images."""
        request = self.context.get('request')
        return [request.build_absolute_uri(gallery.image.url) for gallery in obj.gallery_produits.all()]

class ProductInOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductInOrder
        fields = ['product', 'quantity', 'total_price']
    
    def validate(self, data):
        product = data['product']
        quantity = data['quantity']
        total_price = product.price * quantity
       
        return data

class OrderSerializer(serializers.ModelSerializer):
    items = ProductInOrderSerializer(many=True, write_only=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'customer_fullname', 'customer_phonenumber', 'created_at', 'updated_at', 'status', 'total_price',
            'shipping_address', 'billing_address', 'items'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items')

        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            ProductInOrder.objects.create(order=order, **item_data)

        return order