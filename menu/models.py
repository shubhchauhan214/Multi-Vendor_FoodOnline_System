from django.db import models
from vendor.models import Vendor


# Create your models here.
class Category(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    category_name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Since models are shown in admin panel
    # and tables there are shown with the plural form of the class here
    # When we created Category model here, its plural in admin panel is shown as Categorys
    # that is not correct
    # to correct that we can use verbose function

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def clean(self):
        self.category_name = self.category_name.capitalize()

    def __str__(self):
        return self.category_name


class Product(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    # If we are using category to fetch all the products related to a category
    # We already have a foreign key relationship with Category model
    # but we also need to provide the related_name which is the model name of this model
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='product')
    product_title = models.CharField(max_length=50)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=250, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='foodImages')
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product_title
