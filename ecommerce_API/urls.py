from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NewsletterViewSet, ProductViewSet, OrderViewSet

router = DefaultRouter()
router.register('newsletters', NewsletterViewSet)
router.register('produits', ProductViewSet, basename='product')
router.register('orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
]