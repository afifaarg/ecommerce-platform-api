from rest_framework import viewsets, status
from rest_framework.views import APIView
from .models import Newsletter, Product, Order,InformationMarketing, FAQ, HomeCarouselSection, Client,Fournisseur, ProductInOrder, User, Category, ProductVariant, BuyingBill, ProductInBill, Contact
from .serializers import NewsletterSerializer, InformationMarketingSerializer, FAQSerializer, HomeCarouselSectionSerializer, ClientSerializer, FournisseurSerializer, ProductSerializer, OrderSerializer,ContactSerializer,  UserSerializer, CategorySerializer,ProductInBillSerializer,BuyingBillSerializer
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken  # Optional, for JWT
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.views import TokenBlacklistView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.exceptions import ValidationError
import json
from django.db.models import Sum
import datetime
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist

def dashboard_data(request):
    # Get the total number of clients
    total_clients = Client.objects.count() + User.objects.filter(role="customer").count()

    # Get the total number of orders (commandes)
    total_orders = Order.objects.count()

    # Get the total number of contact forms submitted
    total_contact_forms = Contact.objects.count()  # Assuming 'ouvert' means open/form submitted

    # Get the monthly income (sum of total_amount in Order for each month)
    current_year = datetime.datetime.now().year
    monthly_income = []
    for month in range(1, 13):
        monthly_income.append(
            Order.objects.filter(created_at__year=current_year, created_at__month=month).aggregate(
                total_income=Sum('total_price'))['total_income'] or 0
        )

    # Get the monthly payments (sum of total_price in ProductInBill for each month)
    monthly_payments = []
    for month in range(1, 13):
        monthly_payments.append(
            ProductInBill.objects.filter(
                bill__date__year=current_year, bill__date__month=month).aggregate(
                total_payment=Sum('total_price'))['total_payment'] or 0
        )

    # Prepare the data to return
    data = {
        'clients': total_clients,
        'commandes': total_orders,
        'income': monthly_income,
        'payments': monthly_payments,
        'formulaireContact': total_contact_forms,
    }

    return JsonResponse(data)
class LogoutView(APIView):
    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        print(f"Received Token: {refresh_token}")

        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            print(f"Decoded Token: {token}")
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except ObjectDoesNotExist:
            return Response({"error": "Token not found or already blacklisted"}, status=status.HTTP_400_BAD_REQUEST)
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


class AdminLoginView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")

        if username is None or password is None:
            return Response({'error': 'Please provide both username and password'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        if not user :  # Ensure user has admin role
            return Response({'error': 'Invalid Credentials or not an admin'}, status=status.HTTP_401_UNAUTHORIZED)
        admin_info = User.objects.get(username=username)
        if admin_info.role != 'admin':  # Ensure user has admin role
            return Response({'error': 'Invalid Credentials or not an admin'}, status=status.HTTP_401_UNAUTHORIZED)

        # Generate JWT Token
        refresh = RefreshToken.for_user(user)

        # Fetch admin information
        
        
        response_data = {
            'username': admin_info.username,
            'name': admin_info.full_name,
            'email': admin_info.email,
            'phone': admin_info.phone_number,
            'address': admin_info.address,
            'role': admin_info.role
        }

        return Response({
            'message': 'Admin login successful!',
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

        return super().update(request, *args, **kwargs)

class HomeCarouselSectionViewSet(viewsets.ModelViewSet):
    serializer_class = HomeCarouselSectionSerializer
    def get_queryset(self):
        show = self.request.query_params.get('show', None)

        queryset = HomeCarouselSection.objects.all()

        if show is not None:  
            queryset = queryset.filter(show=show.lower() == 'true')

        return queryset
    
class FAQViewSet(viewsets.ModelViewSet):
    serializer_class = FAQSerializer
    def get_queryset(self):
        show = self.request.query_params.get('show', None)

        queryset = FAQ.objects.all()

        if show is not None:  
            queryset = queryset.filter(show=show.lower() == 'true')

        return queryset

class InformationMarketingViewSet(viewsets.ModelViewSet):
    queryset = InformationMarketing.objects.all()
    serializer_class = InformationMarketingSerializer


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
        print("here")
        serializer = self.get_serializer(data=request.data)
        print("here1")
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            print(e.detail)  # Log or print detailed error messages
        print("here2")
        serializer = OrderSerializer(data=request.data)
        if not serializer.is_valid():
            print("helo",serializer.errors)  # Log the detailed error
            return Response(serializer.errors, status=400)
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
    def post(self, request):
        serializer = FournisseurSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ClientsViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer