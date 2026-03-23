from django.contrib import admin
from menu.models import Category, Product


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('category_name',)}
    list_display = ('category_name', 'vendor', 'updated_at')
    search_fields = ('category_name', 'vendor__vendor_name')


class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('product_title',)}
    list_display = ('product_title', 'category', 'vendor', 'price', 'is_available', 'updated_at')
    search_fields = ('product_title', 'category__category_name', 'vendor__vendor_name')
    list_filter = ('is_available',)


# Register your models here.
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
