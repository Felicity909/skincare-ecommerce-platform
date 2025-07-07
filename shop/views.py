from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, Category, Order, OrderItem, Cart, CartItem
from .serializers import OrderSerializer, CartSerializer, CartItemSerializer
import json

# Product List

def product_list(request):
    products = Product.objects.all().values('id', 'name', 'description', 'price', 'category__name', 'image')
    return JsonResponse(list(products), safe=False)

# Category List

def category_list(request):
    categories = Category.objects.all().values('id', 'name')
    return JsonResponse(list(categories), safe=False)

# Register View

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password)
        return Response({'message': 'User registered successfully!'}, status=status.HTTP_201_CREATED)

# Create Order with Payment Details

class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        items = request.data.get('items', [])
        payment_method = request.data.get('payment_method', 'Mobile Money')

        if not items:
            return Response({'error': 'No items provided'}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(
            user=user,
            payment_method=payment_method,
            payment_status='pending',
            status='pending'
        )

        for item in items:
            try:
                product = Product.objects.get(id=item['product_id'])
                quantity = item.get('quantity', 1)
                OrderItem.objects.create(order=order, product=product, quantity=quantity)
            except Product.DoesNotExist:
                return Response({'error': f"Product with ID {item['product_id']} not found."}, status=404)

        return Response({'message': 'Order created successfully', 'order_id': order.id}, status=201)

# View Orders by User

class UserOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

# Filter Orders

class FilteredOrdersView(ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'payment_status']

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

# Order Detail View

class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=404)

        serializer = OrderSerializer(order)
        return Response(serializer.data)

# Update Payment Info

class UpdatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            order = Order.objects.get(id=pk, user=request.user)
            payment_method = request.data.get('payment_method')
            payment_status = request.data.get('payment_status')

            if payment_method:
                order.payment_method = payment_method
            if payment_status:
                order.payment_status = payment_status

            order.save()
            return Response({'message': 'Payment updated successfully'})
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=404)

# Cart View

# ✅ THIS is the correct one
class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            cart = Order.objects.filter(
                user=request.user,
                status='pending',
                payment_status='pending'
            ).order_by('-created_at').first()

            if not cart:
                return Response({"message": "Your cart is empty."}, status=status.HTTP_200_OK)

            serializer = OrderSerializer(cart)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        product_id = request.data.get('product_id')

        if not product_id:
            return Response({'error': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cart = Order.objects.filter(
                user=request.user,
                status='pending',
                payment_status='pending'
            ).order_by('-created_at').first()

            if not cart:
                return Response({'error': 'No active cart found'}, status=status.HTTP_404_NOT_FOUND)

            item = OrderItem.objects.get(order=cart, product_id=product_id)
            item.delete()

            return Response({'message': 'Item removed from cart'}, status=status.HTTP_200_OK)

        except OrderItem.DoesNotExist:
            return Response({'error': 'Item not found in cart'}, status=status.HTTP_404_NOT_FOUND)


# Add to Cart View (FIXED MULTIPLE OBJECTS ERROR)

class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)

        # FIX: Avoid MultipleObjectsReturned by using .filter().first()
        order = Order.objects.filter(user=user, status='pending', payment_status='pending').order_by('-created_at').first()

        if not order:
            order = Order.objects.create(
                user=user,
                status='pending',
                payment_status='pending'
            )

        order_item, created = OrderItem.objects.get_or_create(order=order, product=product)

        if not created:
            order_item.quantity += quantity
        else:
            order_item.quantity = quantity

        order_item.save()

        return Response({"message": "Product added to cart!"}, status=201)

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Order, OrderItem, Product

class RemoveFromCartView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        product_id = request.data.get('product_id')

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            order = Order.objects.filter(user=user, status='pending', payment_status='pending').latest('created_at')
        except Order.DoesNotExist:
            return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            item = OrderItem.objects.get(order=order, product=product)
            item.delete()
            return Response({"message": "Item removed from cart"}, status=status.HTTP_200_OK)
        except OrderItem.DoesNotExist:
            return Response({"error": "Item not found in cart"}, status=status.HTTP_404_NOT_FOUND)

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Order, OrderItem, CartItem

class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            order = Order.objects.filter(
                user=request.user, status='pending', payment_status='pending'
            ).order_by('-created_at').first()

            if not order:
                return Response({"error": "No pending order found."}, status=400)

            # Mark order as completed
            order.status = 'completed'
            order.payment_status = 'paid'
            order.save()

            #  Clear user's cart after checkout
            CartItem.objects.filter(cart__user=request.user).delete()

            return Response({"message": "Checkout successful!", "order_id": order.id}, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=500)


from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product
from .serializers import ProductSerializer

class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'price']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'name']
    
    from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer, OrderHistorySerializer
from .models import Order

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_data = UserSerializer(user).data
        orders = Order.objects.filter(user=user)
        order_data = OrderHistorySerializer(orders, many=True).data

        return Response({
            "user": user_data,
            "orders": order_data
        })

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ContactMessage
from .serializers import ContactMessageSerializer

class ContactMessageView(APIView):
    def post(self, request):
        data = request.data.copy()
        if request.user.is_authenticated:
            data['user'] = request.user.id

        serializer = ContactMessageSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Message received!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from django.shortcuts import render

def home(request):
    return render(request, 'homepage.html')  # This is your frontend HTML file
