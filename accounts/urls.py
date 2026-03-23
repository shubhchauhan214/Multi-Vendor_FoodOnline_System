from django.urls import path, include
from accounts import views

urlpatterns = [
    path('', views.my_account),
    path('registerUser/', views.register_user, name='register_user'),
    path('registerVendor/', views.register_vendor, name='register_vendor'),

    # Login and Logout pages
    path('login/', views.login, name="login"),
    path('logout/', views.logout, name='logout'),
    path('myAccount/', views.my_account, name='myAccount'),
    path('custDashboard/', views.cust_dashboard, name='custDashboard'),
    path('vendorDashboard/', views.vendor_dashboard, name='vendorDashboard'),

    # Activate user
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('forgot_password/', views.forgot_password, name="forgot_password"),
    path('reset_password_validate/<uidb64>/<token>/', views.reset_password_validate, name="reset_password_validate"),
    path('reset_password/', views.reset_password, name="reset_password"),

    path('vendor/', include('vendor.urls')),
    path('customer/', include('customers.urls')),
]
