from django.urls import path
from marketplace import views

urlpatterns = [
    path('', views.marketplace, name='marketplace'),
    path('<slug:vendor_slug>/', views.vendor_detail, name='vendor_detail'),

    # Add to Cart
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),

    # Remove from Cart
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),

    # Delete item from Cart
    path('delete_from_cart/<int:cart_id>/', views.delete_from_cart, name='delete_from_cart'),
]
