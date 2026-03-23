from django.urls import path
from menu import views

urlpatterns = [
    path('menu-builder/', views.menu_builder, name='menu_builder'),
    path('menu-builder/category/<int:pk>/', views.products_by_category,
         name='products_by_category'),

    # Category CRUD
    path('menu-builder/category/add/', views.add_category, name='add_category'),
    path('menu-builder/category/edit/<int:category_id>', views.edit_category, name='edit_category'),
    path('menu-builder/category/delete/<int:category_id>', views.delete_category, name='delete_category'),

    # Product CRUD
    path('menu-builder/product/add/', views.add_product, name='add_product'),
    path('menu-builder/product/add/<int:category_id>', views.add_product, name='add_product_for_category'),
    path('menu-builder/product/edit/<int:product_id>', views.edit_product, name='edit_product'),
    path('menu-builder/product/delete/<int:product_id>', views.delete_product, name='delete_product'),
]
