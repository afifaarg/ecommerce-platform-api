from rest_framework import serializers
from .models import Newsletter, ProductGallery, Product, Category, Order, ProductInOrder, User, ProductVariant
from rest_framework_simplejwt.tokens import RefreshToken
import json

class BlacklistTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs['refresh_token']
        return attrs

    def save(self, **kwargs):
        try:
            # Use the refresh token to blacklist it
            token = RefreshToken(self.token)
            token.blacklist()
        except Exception as e:
            self.fail('bad_token')
            
class NewsletterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Newsletter
        fields = ['email']  

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id','username','email', 'password', 'full_name', 'address', 'phone_number', 'role']

    def create(self, validated_data):  
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user   
       
class ProductGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductGallery
        fields = ['image']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','name','description']

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id', 'product', 'color', 'dimension', 'variant_price']

class ProductSerializer(serializers.ModelSerializer):
    gallery_images = serializers.SerializerMethodField()
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())  # Ensure it's an ID
    image = serializers.SerializerMethodField()
    variants = ProductVariantSerializer(many=True, required=False) 

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
            'image',
            'tva',
            'in_stock',
            'is_active',
            'created_at',
            'promo',
            'promo_video',
            'gallery_images',
            'variants',  # Include variant details if you have a Variant model
        ]
        extra_kwargs = {
            'variants': {'required': False},
        }

    def get_category(self, obj):
        return obj.category.name  # Return the category name, if needed

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None

    def get_gallery_images(self, obj):
        request = self.context.get('request')
        return [request.build_absolute_uri(gallery.image.url) for gallery in obj.gallery_produits.all()]

    def create(self, validated_data):
        # Get the gallery images from the request
        gallery_images = self.context['request'].FILES.getlist('gallery_images')

        # Create the Product instance (without gallery images first)
        instance = super().create(validated_data)

        # Associate gallery images with the product
        for image in gallery_images:
            ProductGallery.objects.create(product=instance, image=image)

        variants_products = [json.loads(variant) for variant in self.context["request"].POST.getlist('variants')]
        # Now create the variants
        for variant in variants_products:
            if variant["type"] == "text":
                ProductVariant.objects.create(product=instance, dimension=variant["value"], variant_price=variant["variant_price"])
            else:
                ProductVariant.objects.create(product=instance, color=variant["value"], variant_price=variant["variant_price"])
        return instance

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
