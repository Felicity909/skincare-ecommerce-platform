from .views import ProductDetailView, signin_view, product_detail, cart_page, checkout_page
from django.urls import path
from django.views.generic import TemplateView
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
    home
)

urlpatterns = [
    # API Auth
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Cart
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add/', AddToCartView.as_view(), name='add-to-cart'),
    path('api/cart/remove/', RemoveFromCartView.as_view(), name='remove-from-cart'),

    # Cart page (frontend)
    path('cart-page/', cart_page, name='cart-page'),

    # Orders
    path('orders/create/', CreateOrderView.as_view(), name='create-order'),
    path('orders/', UserOrdersView.as_view(), name='user-orders'),
    path('orders/filter/', FilteredOrdersView.as_view(), name='filter-orders'),
    path('orders/<int:order_id>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/<int:pk>/payment/', UpdatePaymentView.as_view(), name='update-payment'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),

    # Products & Profile
    path('products/', ProductListView.as_view(), name='product-list'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('contact/', ContactMessageView.as_view(), name='contact-message'),

    # Frontend pages
    path('', home, name='home'),
path('shop/', TemplateView.as_view(template_name="shop/productpage.html"), name="shop"),
path('signin/', signin_view, name="signin"),
path('checkout-page/', checkout_page, name='checkout-page'),
    path('blog/', TemplateView.as_view(template_name="shop/blog.html"), name="blog"),
    path('about/', TemplateView.as_view(template_name="shop/about.html"), name="about"),
path('product/<int:pk>/', product_detail, name='product-detail'),
]


