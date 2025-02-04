from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import dashboard_data,AdminLoginView, NewsletterViewSet, FAQViewSet,InformationMarketingViewSet, HomeCarouselSectionViewSet, ProductViewSet,ClientsViewSet, FournisseurViewSet, OrderViewSet,UserViewSet, ContactViewSet, LoginView, LogoutView, CategoriesViewSet, BuyingBillViewSet

router = DefaultRouter()
router.register('newsletters', NewsletterViewSet)
router.register('produits', ProductViewSet, basename='product')
router.register('orders', OrderViewSet, basename='order')
router.register('signup', UserViewSet, basename='signup')
router.register('categories', CategoriesViewSet, basename='categories')
router.register('buyingBills', BuyingBillViewSet, basename='buyingBills')
router.register('contact', ContactViewSet, basename='contact')
router.register('fournisseurs', FournisseurViewSet, basename='fournisseurs')
router.register('clients', ClientsViewSet, basename='clients')
router.register('banners', HomeCarouselSectionViewSet, basename='banners')
router.register('faqSection', FAQViewSet, basename='faqSection')
router.register('maketingInfo', InformationMarketingViewSet, basename='maketingInfo')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view()),
    path('loginAdmin/', AdminLoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('dashboard/', dashboard_data, name='dashboard_data'),
]