from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.template.defaultfilters import slugify
from accounts.views import check_role_vendor
from menu.forms import CategoryForm, ProductForm
from menu.models import Category, Product
from vendor.utils import get_vendor


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def menu_builder(request):
    vendor = get_vendor(request)
    categories = Category.objects.filter(vendor=vendor).order_by('created_at')
    context = {
        'categories': categories,
    }
    return render(request, 'menu/menu_builder.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def products_by_category(request, pk=None):
    vendor = get_vendor(request)
    category = get_object_or_404(Category, pk=pk)
    products = Product.objects.filter(vendor=vendor, category=category)
    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'menu/products_by_category.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        try:
            if form.is_valid():
                category_name = form.cleaned_data['category_name']
                category = form.save(commit=False)
                # Before finally saving the form, we need to get vendor and slug details
                category.vendor = get_vendor(request)
                category.slug = slugify(category_name)+'-'+str(category.vendor.id)
                form.save()
                messages.success(request, "Category created successfully!")
                return redirect('menu_builder')
        except:
            messages.error(request, "Category with same name already exists.")
    else:
        form = CategoryForm
    context = {
        'form': form,
    }
    return render(request, 'menu/category/add.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_category(request, category_id=None):
    category = get_object_or_404(Category, pk=category_id)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        try:
            if form.is_valid():
                category = form.save(commit=False)
                # Before finally saving the form, we need to get vendor and slug details
                category.vendor = get_vendor(request)
                category.slug = slugify(category.category_name)+'-'+str(category.vendor.id)
                form.save()
                messages.success(request, "Category updated successfully!")
                return redirect('menu_builder')
        except:
            messages.error(request, "Category with same name already exists.")
    else:
        form = CategoryForm(instance=category)
    context = {
        'form': form,
        'category': category,
    }
    return render(request, 'menu/category/edit.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_category(request, category_id=None):
    category = get_object_or_404(Category, pk=category_id)
    category.delete()
    messages.success(request, 'Category has been deleted successfully!')
    return redirect('menu_builder')


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_product(request, category_id=None):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            # Before finally saving the form, we need to get vendor and slug details
            product.vendor = get_vendor(request)
            product.slug = slugify(product.product_title)
            form.save()
            messages.success(request, "Product created successfully!")
            return redirect('products_by_category', product.category.id)
    else:
        if category_id:
            category = get_object_or_404(Category, pk=category_id)
            form = ProductForm(initial={'category': category})
        else:
            form = ProductForm()

        # Modify form field here so that it contains categories of active vendor only.
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))

    context = {
        'form': form,
    }
    return render(request, 'menu/product/add.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            # Before finally saving the form, we need to get vendor and slug details
            product.vendor = get_vendor(request)
            product.slug = slugify(product.product_title)
            form.save()
            messages.success(request, "Product updated successfully!")
            return redirect('products_by_category', product.category.id)
    else:
        form = ProductForm(instance=product)

        # Modify form field here so that it contains categories of active vendor only.
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))

    context = {
        'form': form,
        'product': product,
    }
    return render(request, 'menu/product/edit.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    category_id = product.category.id
    product.delete()
    messages.success(request, 'Product has been deleted successfully!')
    return redirect('products_by_category', category_id)
