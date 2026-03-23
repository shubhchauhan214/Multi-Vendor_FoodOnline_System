from django.urls import path, include
from vendor import views
from accounts import views as account_views

urlpatterns = [
    path('', account_views.vendor_dashboard, name='vendor'),
    path('profile/', views.profile, name='vendor_profile'),

    # Category CRUD
    path('menu/', include('menu.urls')),

    # Opening Hours
    path('opening-hours/', views.opening_hours, name='opening_hours'),
    path('opening-hours/add/', views.add_opening_hours, name='add_opening_hours'),
    path('opening-hours/remove/<int:pk>/', views.remove_opening_hours, name='remove_opening_hours'),

    # Order Details
    path('order_details/<int:order_number>/', views.order_details, name='vendor_order_details'),
    path('my_orders/', views.my_orders, name='vendor_my_orders'),
]
