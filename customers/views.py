import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from accounts.models import UserProfile
from accounts.views import check_role_customer
from accounts.forms import CustomerProfileForm, UserInfoForm
from orders.models import Order, OrderedProduct


@login_required(login_url='login')
@user_passes_test(check_role_customer)
def profile(request):
    existing_profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == "POST":
        profile_form = CustomerProfileForm(request.POST, request.FILES, instance=existing_profile)
        user_form = UserInfoForm(request.POST, instance=request.user)
        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('cust_profile')
        else:
            print(profile_form.errors)
            print(user_form.errors)
    else:
        profile_form = CustomerProfileForm(instance=existing_profile)
        user_form = UserInfoForm(instance=request.user)

    context = {
        'profile_form': profile_form,
        'user_form': user_form,
        'profile': existing_profile
    }

    return render(request, 'customers/profile.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_customer)
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    context = {
        'orders': orders
    }

    return render(request, 'customers/my_orders.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_customer)
def order_details(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderedProduct.objects.filter(order=order)

        subtotal = 0
        for item in ordered_products:
            subtotal += (item.price * item.quantity)

        tax_data = json.loads(order.tax_data)

        context ={
            'order': order,
            'ordered_product': ordered_products,
            'subtotal': subtotal,
            'tax_data': tax_data
        }

        return render(request, 'customers/order_details.html', context)
    except:
        return redirect('customer')

