from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView,
    CreateOrderView,
    UserOrdersView,
    FilteredOrdersView,
    OrderDetailView,
    UpdatePaymentView,
    CartView,
    AddToCartView,
    RemoveFromCartView,
    CheckoutView,
    ProductListView,
    UserProfileView,
    ContactMessageView,
)

urlpatterns = [
    # Auth
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
   
    #Cart
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add/', AddToCartView.as_view(), name='add-to-cart'),

    # Orders
    path('orders/create/', CreateOrderView.as_view(), name='create-order'),
    path('orders/', UserOrdersView.as_view(), name='user-orders'),
    path('orders/filter/', FilteredOrdersView.as_view(), name='filter-orders'),
    path('orders/<int:order_id>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/<int:pk>/payment/', UpdatePaymentView.as_view(), name='update-payment'),
    path('api/cart/remove/', RemoveFromCartView.as_view(), name='remove-from-cart'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('contact/', ContactMessageView.as_view(), name='contact-message'),
]
from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name="homepage.html"), name="home"),
    path('shop/', TemplateView.as_view(template_name="productpage.html"), name="shop"),
    path('signin/', TemplateView.as_view(template_name="signin.html"), name="signin"),
    path('checkout/', TemplateView.as_view(template_name="checkout.html"), name="checkout"),
    path('blog/', TemplateView.as_view(template_name="blog.html"), name="blog"),
    path('about/', TemplateView.as_view(template_name="about.html"), name="about"),
]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
]


