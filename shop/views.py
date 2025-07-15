from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Product, Category, Order, OrderItem, CartItem, ContactMessage

# Homepage

def home(request):
    return render(request, 'shop/homepage.html')
# Sign In View

def signin_view(request):
    error = None
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            error = "Invalid email or password."
    return render(request, "shop/signin.html", {"error": error})

# Register View

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        else:
            User.objects.create_user(username=username, password=password)
            messages.success(request, "User registered successfully!")
            return redirect("signin")

    return render(request, "shop/register.html")

# Product List View

def product_list_view(request):
    products = Product.objects.all()
    return render(request, 'shop/productpage.html', {'products': products})

# Product Detail View

def product_detail_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'shop/productdetails.html', {'product': product})

# Category List

def category_list_view(request):
    categories = Category.objects.all()
    return render(request, 'shop/category_list.html', {'categories': categories})

# Cart Page View

@login_required
def cart_page(request):
    user = request.user
    order = Order.objects.filter(user=user, status='pending', payment_status='pending').order_by('-created_at').first()
    cart_items = []
    total = 0
    if order:
        cart_items = OrderItem.objects.filter(order=order)
        total = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'shop/cart.html', {'cart_items': cart_items, 'total': total})

# Add to Cart View

@login_required
def add_to_cart_view(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        quantity = int(request.POST.get("quantity", 1))

        product = get_object_or_404(Product, id=product_id)
        order = Order.objects.filter(user=request.user, status='pending', payment_status='pending').order_by('-created_at').first()

        if not order:
            order = Order.objects.create(user=request.user, status='pending', payment_status='pending')

        order_item, created = OrderItem.objects.get_or_create(order=order, product=product)
        order_item.quantity = order_item.quantity + quantity if not created else quantity
        order_item.save()

        messages.success(request, "Product added to cart!")
    return redirect("product_list")

# Remove from Cart View

@login_required
def remove_from_cart_view(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        order = Order.objects.filter(user=request.user, status='pending', payment_status='pending').latest('created_at')
        item = OrderItem.objects.get(order=order, product=product)
        item.delete()
        messages.success(request, "Item removed from cart.")
    except:
        messages.error(request, "Item could not be removed.")
    return redirect("cart")

# Checkout Page

@login_required
def checkout_page(request):
    user = request.user
    order = Order.objects.filter(user=user, status='pending', payment_status='pending').order_by('-created_at').first()
    cart_items = []
    total = 0
    if order:
        cart_items = OrderItem.objects.filter(order=order)
        total = sum(item.product.price * item.quantity for item in cart_items)

    if request.method == 'POST':
        if order:
            order.status = 'completed'
            order.payment_status = 'paid'
            order.save()
            CartItem.objects.filter(cart__user=user).delete()
            messages.success(request, 'Checkout successful!')
            return render(request, 'shop/checkout.html', {'cart_items': [], 'total': 0, 'success': True})
        else:
            messages.error(request, 'No items in cart to checkout.')
            return render(request, 'shop/checkout.html', {'cart_items': [], 'total': 0, 'error': True})

    return render(request, 'shop/checkout.html', {'cart_items': cart_items, 'total': total})

# User Orders View

@login_required
def user_orders_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, "shop/order_history.html", {"orders": orders})

# Order Detail View

@login_required
def order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "shop/order_detail.html", {"order": order})

# Update Payment View

@login_required
def update_payment_view(request, pk):
    order = get_object_or_404(Order, id=pk, user=request.user)

    if request.method == "POST":
        order.payment_method = request.POST.get("payment_method", order.payment_method)
        order.payment_status = request.POST.get("payment_status", order.payment_status)
        order.save()
        messages.success(request, "Payment updated successfully.")

    return redirect("order_detail", order_id=pk)

# Contact Message View

def contact_message_view(request):
    if request.method == "POST":
        content = request.POST.get("message")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        name = request.POST.get("name")

        msg = ContactMessage.objects.create(
            name=name, email=email, phone=phone, message=content,
            user=request.user if request.user.is_authenticated else None
        )
        messages.success(request, "Message received!")
        return redirect("contact")
    return render(request, "shop/contact.html")

# User Profile View

@login_required
def profile_view(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, "shop/profile.html", {
        "user": request.user,
        "orders": orders
    })
