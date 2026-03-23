from django.urls import path
from customers import views
from accounts import views as accounts_views

urlpatterns = [
    path('', accounts_views.cust_dashboard, name='custDashboard'),
    path('profile/', views.profile, name='cust_profile'),
    path('my_orders/', views.my_orders, name='my_orders'),
    path('order_details/<int:order_number>/', views.order_details, name='order_details'),
]