from rest_framework import serializers
from .models import Newsletter, ProductGallery, Product, Category, Order, ProductInOrder, Contact, User, ProductVariant, BuyingBill, ProductInBill
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ObjectDoesNotExist
import json
from django.db import transaction

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
        fields = ['id','username', 'password', 'full_name', 'address', 'phone_number', 'role']

    def create(self, validated_data):  
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user   

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'nom', 'email', 'message', 'etat']


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
    available_quantity = serializers.SerializerMethodField()
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
            'available_quantity',
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

    def get_available_quantity(self, obj):
        # Calculate total quantity bought (from BuyingBill) and quantity sold (from Orders)
        total_quantity_bought = sum(item.quantity for item in obj.productinbill_set.all())
        total_quantity_sold = sum(item.quantity for item in obj.productinorder_set.all())

        # Calculate available quantity
        available_quantity = total_quantity_bought - total_quantity_sold
        return max(available_quantity, 0)  # Ensure it doesn’t go below zero
    
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

    def update(self, instance, validated_data):
        # Update the product fields
        print("instance2")
        instance.name = validated_data.get('name', instance.name)
        instance.category = validated_data.get('category', instance.category)
        instance.description = validated_data.get('description', instance.description)
        instance.reference = validated_data.get('reference', instance.reference)
        instance.price = validated_data.get('price', instance.price)
        instance.cost_price = validated_data.get('cost_price', instance.cost_price)
        instance.margin = validated_data.get('margin', instance.margin)
        instance.tva = validated_data.get('tva', instance.tva)
        instance.in_stock = validated_data.get('in_stock', instance.in_stock)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.promo = validated_data.get('promo', instance.promo)

        # Handling the image field update (if needed)
        if 'image' in validated_data:
            instance.image = validated_data.get('image', instance.image)

        # Handle the gallery images (ensure they are passed as files)
        gallery_images = self.context['request'].FILES.getlist('gallery_images')
        if gallery_images:
            print("here")
            # Delete existing images if needed before adding new ones
            instance.gallery_produits.all().delete()
            for image in gallery_images:
                ProductGallery.objects.create(product=instance, image=image)

        # Handling variants (parse from POST data)
        variants_products = json.loads(self.context["request"].POST.get('variants', '[]'))
        instance.variants.all().delete()  # Clear previous variants
        for variant in variants_products:
            if variant["type"] == "text":
                ProductVariant.objects.create(product=instance, dimension=variant["value"], variant_price=variant["variant_price"])
            else:
                ProductVariant.objects.create(product=instance, color=variant["value"], variant_price=variant["variant_price"])

        # Handling the promo video (if it exists)
        if 'promo_video' in validated_data:
            instance.promo_video = validated_data.get('promo_video', instance.promo_video)

        # Save the instance and return it
        instance.save()
        return instance
    
class ProductInOrderSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)  # Assuming 'name' is a field on Product model
    product_reference = serializers.CharField(source='product.reference', read_only=True)  # Assuming 'name' is a field on Product model
    prix_unitaire = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    total_price = serializers.SerializerMethodField()  # Calculated field

    class Meta:
        model = ProductInOrder
        fields = ['product_reference','product_name', 'prix_unitaire', 'quantity', 'total_price']

    def get_total_price(self, obj):
        return obj.product.price * obj.quantity

class OrderSerializer(serializers.ModelSerializer):
    items = ProductInOrderSerializer(many=True)
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

    def update(self, instance, validated_data):
        # Update simple fields, including status
        for attr, value in validated_data.items():
            if attr != 'items':  # Avoid updating items directly in this loop
                setattr(instance, attr, value)
        instance.save()

        # Handle items if provided
        items_data = validated_data.get('items')
        if items_data is not None:
            # Clear existing items and re-add new items
            instance.items.all().delete()
            for item_data in items_data:
                ProductInOrder.objects.create(order=instance, **item_data)

        return instance
    
# Serializer for BuyingBill
from rest_framework import serializers
from .models import BuyingBill, ProductInBill, Product

class ProductInBillSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())  # Accept product ID directly
    reference = serializers.CharField(source='product.reference', read_only=True)  # Read-only, derived from product
    name = serializers.CharField(source='product.name', read_only=True)  # Read-only, derived from product

    class Meta:
        model = ProductInBill
        fields = ['product', 'reference', 'name', 'quantity', 'unit_price', 'total_price']

    def validate(self, data):
        # Ensure quantity and unit_price are numbers
        data['quantity'] = int(data['quantity'])
        data['unit_price'] = float(data['unit_price'])
        
        # Calculate total_price if not provided
        if not data.get('total_price'):
            data['total_price'] = data['unit_price'] * data['quantity']
        return data

class BuyingBillSerializer(serializers.ModelSerializer):
    products = ProductInBillSerializer(many=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = BuyingBill
        fields = ['id', 'bill_id', 'date', 'payment_method', 'is_paid', 'total_amount', 'fournisseur', 'products']

    @transaction.atomic
    def create(self, validated_data):
        # Pop products data and initialize the total_amount
        products_data = validated_data.pop('products')
        buying_bill = BuyingBill.objects.create(total_amount=0, **validated_data)

        total_amount = 0
        # Iterate through products, create ProductInBill instances, and calculate total_amount
        for product_data in products_data:
            product_instance = product_data.pop('product')  # Extract product instance
            product_in_bill = ProductInBill.objects.create(
                bill=buying_bill,
                product=product_instance,
                **{k: v for k, v in product_data.items() if k in ['quantity', 'unit_price', 'total_price']}  # Handle only relevant fields
            )
            total_amount += product_in_bill.total_price

        # Set total_amount in BuyingBill and save
        buying_bill.total_amount = total_amount
        buying_bill.save()
        
        return buying_bill

    @transaction.atomic
    def update(self, instance, validated_data):
        # Update basic fields first
        products_data = validated_data.pop('products', None)
        if 'total_amount' in validated_data:
            instance.total_amount = validated_data['total_amount']
        
        # Update fields like fournisseur and payment_method
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # If there are any product updates, handle them
        if products_data is not None:
            # Delete existing product entries if necessary
            instance.products.all().delete()

            # Recreate products with the updated data
            total_amount = 0
            for product_data in products_data:
                product_instance = product_data.pop('product')
                product_in_bill = ProductInBill.objects.create(
                    bill=instance,
                    product=product_instance,
                    **{k: v for k, v in product_data.items() if k in ['quantity', 'unit_price', 'total_price']}
                )
                total_amount += product_in_bill.total_price

            # Update total_amount after product updates
            instance.total_amount = total_amount

        instance.save()
        return instance