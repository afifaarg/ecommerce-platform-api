from rest_framework import viewsets, status
from .models import Newsletter, Product, Order, ProductInOrder
from .serializers import NewsletterSerializer, ProductSerializer, OrderSerializer
from rest_framework.response import Response
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    def get_serializer_context(self):
        # Pass the request to the serializer context
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    
class NewsletterViewSet(viewsets.ModelViewSet):
    queryset = Newsletter.objects.all()
    serializer_class = NewsletterSerializer
    
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):
        # Use the serializer to validate and create an order
        print('hello')
        serializer = self.get_serializer(data=request.data)
        print("hello1")
        serializer.is_valid(raise_exception=True)
        print("hello2")
        # Create the order instance
        order = serializer.save()

        # Handle creating ProductInOrder instances
        items_data = request.data.get('items', [])
        for item_data in items_data:
            # Ensure to include the order reference while creating ProductInOrder
            ProductInOrder.objects.create(
                order=order,
                product_id=item_data['product'],  # Assuming product is passed as ID
                quantity=item_data['quantity'],
                total_price=item_data['total_price'],
            )

        # Return the created order instance
        return Response(serializer.data, status=status.HTTP_201_CREATED)