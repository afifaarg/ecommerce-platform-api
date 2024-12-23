from rest_framework import viewsets, status
from rest_framework.views import APIView
from .models import Newsletter, Product, Order, HomeCarouselSection, Client,Fournisseur, ProductInOrder, User, Category, ProductVariant, BuyingBill, ProductInBill, Contact
from .serializers import NewsletterSerializer,HomeCarouselSectionSerializer, ClientSerializer, FournisseurSerializer, ProductSerializer, OrderSerializer,ContactSerializer,  UserSerializer, CategorySerializer,ProductInBillSerializer,BuyingBillSerializer
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken  # Optional, for JWT
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.views import TokenBlacklistView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.exceptions import ValidationError
import json
class LogoutView(APIView):
    def post(self, request):
        refresh_token = request.data.get("refresh_token")  # Get refresh token from the request body
        print(request.data)
        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @transaction.atomic  # Ensure that all saves are part of the same transaction
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True) 
        # Ensure required fields are present
        if not all([
            'username' in request.data,
            'password' in request.data,
            'full_name' in request.data,
        ]):
            return Response({'error': 'Missing required fields: username, password, full_name'}, status=status.HTTP_400_BAD_REQUEST)

        # Save the main user profile
        user = serializer.save()
       
        # Generate JWT tokens for the user
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "user": UserSerializer(user).data,
            "refresh_token": str(refresh),
            "access_token": str(refresh.access_token),
            "message": "User registered successfully"
        }, status=status.HTTP_201_CREATED)
    
class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")

        if username is None or password is None:
            return Response({'error': 'Please provide both username and password'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)

        if not user:
            print("wrong credentials")
            return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        # Optional: Generate JWT Token
        refresh = RefreshToken.for_user(user)

        # Fetch user information
        loginInfomations = user
        yourInfo = User.objects.get(username=username)  # Ensure user is an instance of PlatformUser
        # Prepare response data
        response_data = {
            'username': loginInfomations.username,
            'name': yourInfo.full_name,
            'email': yourInfo.email,  # Ensure you have this field in your PlatformUser model
            'phone': yourInfo.phone_number,
            'address': yourInfo.address,
        }

        return Response({
            'message': 'Login successful!',
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_data': response_data
        }, status=status.HTTP_200_OK)
        
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    def get_serializer_context(self):
        # Pass the request to the serializer context
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def create(self, request, *args, **kwargs):
        # Create the variants instances
        
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        print(self.request.POST)
        return super().update(request, *args, **kwargs)

class HomeCarouselSectionViewSet(viewsets.ModelViewSet):
    queryset = HomeCarouselSection.objects.all()
    serializer_class = HomeCarouselSectionSerializer
    
class NewsletterViewSet(viewsets.ModelViewSet):
    queryset = Newsletter.objects.all()
    serializer_class = NewsletterSerializer

class CategoriesViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
     
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
class BuyingBillViewSet(viewsets.ModelViewSet):
    queryset = BuyingBill.objects.all()
    serializer_class = BuyingBillSerializer

class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

class FournisseurViewSet(viewsets.ModelViewSet):
    queryset = Fournisseur.objects.all()
    serializer_class = FournisseurSerializer

class ClientsViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer