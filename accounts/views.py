import datetime

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.template.defaultfilters import slugify
from django.utils.http import urlsafe_base64_decode
from accounts.forms import UserForm
from accounts.models import User, UserProfile
from django.contrib import messages, auth
from accounts.utils import detect_user, send_mail
from orders.models import Order
from vendor.forms import VendorForm
from vendor.models import Vendor


# Create Decorator to restrict vendor from accessing customer page
def check_role_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied


# Create decorator to restrict customer from accessing vendor page
def check_role_customer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied


# Create your views here.
def register_user(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in.")
        return redirect('myAccount')
    elif request.method == "POST":
        print(request.POST)
        form = UserForm(request.POST)
        if form.is_valid():
            # Two ways to save the user.
            # 1. Use form to save user directly
            # 2. use create_user function from UserManager class.

            # Create user using the form
            # password = form.cleaned_data['password']
            # user = form.save(commit=False)
            # user.set_password(password)
            # user.role = User.CUSTOMER
            # user.save()

            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name, last_name, username, email, password)
            user.role = User.CUSTOMER
            user.save()
            # this could be improved. as create_user already saved the user in db and returned that user
            # we are updating one value i.e. role here for that user and saving it again in db.
            # this is creating an extra db hit.

            # Send verification mail
            mail_subject = 'Email Verification for FoodOnline'
            email_template = 'accounts/email/account_verification_email.html'
            send_mail(request, user, mail_subject, email_template)
            print("User is created.")
            messages.success(request, 'Your account has been registered successfully. Please verify the email to '
                                      'activate the account.')
            return redirect('register_user')
        else:
            print("invalid form")
            print(form.errors)
    else:
        form = UserForm()
    context = {
        'form': form
    }
    return render(request, 'accounts/registerUser.html', context)


def register_vendor(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in.")
        return redirect('myAccount')
    elif request.method == "POST":
        # store the data and create the vendor
        form = UserForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES)
        if form.is_valid() and v_form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name, last_name, username, email, password)
            user.role = User.VENDOR
            user.save()

            vendor = v_form.save(commit=False)
            vendor.user = user
            vendor_name = v_form.cleaned_data['vendor_name']
            vendor.vendor_slug = slugify(vendor_name)+'-'+str(user.id)
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()

            # Send verification mail
            mail_subject = 'Email Verification for FoodOnline'
            email_template = 'accounts/email/vendor_account_verification_email.html'
            send_mail(request, user, mail_subject, email_template)
            messages.success(request, 'Your account has been registered successfully. Please verify the email to '
                                      'activate the account.')
            return redirect('register_vendor')
        else:
            print('invalid forms')
            print(form.errors)
    else:
        form = UserForm()
        v_form = VendorForm()
    context = {
        'form': form,
        'v_form': v_form
    }
    return render(request, 'accounts/registerVendor.html', context)


def login(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in.")
        return redirect('myAccount')
    # first we will check if the request is post
    elif request.method == "POST":
        # Get email and password from the form using name of the html tags
        email = request.POST['email']
        password = request.POST['password']

        # check if the email and password belongs to any user
        # we will use inbuilt authenticate method to do this.
        user = auth.authenticate(email=email, password=password)
        if user is not None:
            auth.login(request, user)
            messages.success(request, "You are now logged in.")
            return redirect('myAccount')
        else:
            messages.error(request, "Invalid login credentials.")
            return redirect('login')
    return render(request, 'accounts/login.html')


def logout(request):
    auth.logout(request)
    messages.info(request, 'You are logged out.')
    return redirect("login")


@login_required(login_url='login')
def my_account(request):
    user = request.user
    redirect_url = detect_user(user)
    return redirect(redirect_url)


@login_required(login_url='login')
@user_passes_test(check_role_customer)
def cust_dashboard(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True)
    recent_orders = orders[:5]
    context = {
        'orders': recent_orders,
        'orders_count': orders.count()
    }
    return render(request, 'accounts/cust_dashboard.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendor_dashboard(request):
    vendor = Vendor.objects.get(user=request.user)
    orders = Order.objects.filter(vendors__in=[vendor.id], is_ordered=True)\
        .order_by('-created_at')
    recent_orders = orders[:5]

    # total revenue
    total_revenue = 0
    for i in orders:
        total_revenue += i.total


    # Current month revenue
    current_month = datetime.datetime.now().month
    current_month_orders = orders.filter(vendors__in=[vendor.id], created_at__month=current_month)
    current_month_revenue = 0
    for i in current_month_orders:
        current_month_revenue += i.total


    context = {
        'orders': recent_orders,
        'orders_count': orders.count(),
        'total_revenue': total_revenue,
        'current_month_revenue': current_month_revenue,
    }
    return render(request, 'accounts/vendor_dashboard.html', context)


def activate(request, uidb64, token):
    # activate the user by setting the is_active to true
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Congratulations! Your account is activated.")
        return redirect('myAccount')
    else:
        messages.error(request, "Invalid activation link.")
        return redirect('myAccount')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)

            # send reset password email
            mail_subject = 'Reset Password for FoodOnline'
            email_template = 'accounts/email/reset_password_email.html'
            send_mail(request, user, mail_subject, email_template)
            messages.success(request, "Password reset link has been sent to your email address.")
            return redirect('login')
        else:
            messages.error(request, "Your search did not return any results. Please try again with other information.")
            return redirect('forgot_password')
    return render(request, 'accounts/forgot_password.html')


def reset_password_validate(request, uidb64, token):
    # validate the user by decoding the token and user primary key
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        # messages.info(request, "Please reset your password.")
        return redirect('reset_password')
    else:
        messages.error(request, 'This link has been expired.')
        return redirect('myAccount')


# As of now, I can directly open the reset_password URL in browser. That should not be the case.
def reset_password(request):
    if request.method == "POST":
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            pk = request.session.get('uid')
            user = User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request, 'Password updated successfully.')
            return redirect('login')
        else:
            messages.error(request, 'Passwords do not match.')
            return redirect('reset_password')
    return render(request, 'accounts/reset_password.html')

