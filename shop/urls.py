from .views import *
from django.urls import path
urlpatterns = [
    path('', home, name='home'),
    path('products/', product_list_view, name='product_list'),
    path('product/<int:pk>/', product_detail_view, name='product_detail'),
    path('cart/', cart_page, name='cart'),
    path('cart/add/', add_to_cart_view, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', remove_from_cart_view, name='remove_from_cart'),
    path('checkout/', checkout_page, name='checkout'),
    path('orders/', user_orders_view, name='orders'),
    path('order/<int:order_id>/', order_detail_view, name='order_detail'),
    path('order/<int:pk>/payment/', update_payment_view, name='update_payment'),
    path('contact/', contact_message_view, name='contact'),
    path('profile/', profile_view, name='profile'),
    path('register/', register_view, name='register'),
    path('signin/', signin_view, name='signin'),
]
