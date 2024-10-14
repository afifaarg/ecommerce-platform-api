from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NewsletterViewSet, ProductViewSet

router = DefaultRouter()
router.register('newsletters', NewsletterViewSet)
router.register('produits', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
]