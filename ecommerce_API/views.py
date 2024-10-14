from rest_framework import viewsets
from .models import Newsletter, Product
from .serializers import NewsletterSerializer, ProductSerializer

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