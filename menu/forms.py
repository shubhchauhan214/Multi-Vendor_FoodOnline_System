from django import forms
from menu.models import Category, Product
from vendor.validators import allow_only_images_validator


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'description']


class ProductForm(forms.ModelForm):
    image = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info w-100'}),
                            validators=[allow_only_images_validator])

    class Meta:
        model = Product
        fields = ['category', 'product_title', 'description', 'price', 'image', 'is_available']
