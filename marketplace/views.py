from django.contrib.auth.decorators import login_required
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.db.models import Prefetch, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from accounts.models import UserProfile
from marketplace.context_processors import get_cart_counter, get_cart_amount
from marketplace.models import Cart
from menu.models import Category, Product
from orders.forms import OrderForm
from vendor.models import Vendor, OpeningHour
from django.contrib.gis.db.models.functions import Distance
from datetime import date, datetime

def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendor_count = vendors.count()
    context = {
        'vendors': vendors,
        'vendor_count': vendor_count
    }
    return render(request, 'marketplace/listings.html', context)


def vendor_detail(request, vendor_slug):
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)

    # We have Products model have foreign key relationship to Category model
    # but we do not have Category model having any relationship with Products
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch('product', queryset=Product.objects.filter(is_available=True))
    )

    opening_hours = OpeningHour.objects.filter(vendor=vendor).order_by('day', '-from_hour')

    # Check current day's opening hours
    today_date_weekday = date.today().isoweekday()
    current_opening_hours = OpeningHour.objects.filter(vendor=vendor, day=today_date_weekday)

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None

    context = {
        'vendor': vendor,
        'categories': categories,
        'cart_items': cart_items,
        'opening_hours': opening_hours,
        'current_opening_hours': current_opening_hours
    }
    return render(request, 'marketplace/vendor_detail.html', context)


def add_to_cart(request, product_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Check if the product exists
            try:
                prod = Product.objects.get(id=product_id)
                # Check if the user has already added product in the cart
                try:
                    chkCart = Cart.objects.get(user=request.user, products=prod)
                    # Increase the cart quantity
                    chkCart.quantity += 1
                    chkCart.save()
                    return JsonResponse(
                        {'status': 'Success',
                         'message': 'Product increased in cart.',
                         'cart_counter': get_cart_counter(request),
                         'qty': chkCart.quantity,
                         'cart_amount': get_cart_amount(request)
                         }
                    )
                except:
                    # check if any cart for this user
                    try:
                        any_cart_items = Cart.objects.filter(user=request.user)[:1].get()
                        existing_vendor_id = any_cart_items.products.vendor.id
                        if prod.vendor.id == existing_vendor_id:
                            chkCart = Cart.objects.create(user=request.user, products=prod, quantity=1)
                            return JsonResponse(
                                {'status': 'Success',
                                 'message': 'Product added to the cart.',
                                 'cart_counter': get_cart_counter(request),
                                 'qty': chkCart.quantity,
                                 'cart_amount': get_cart_amount(request)
                                 }
                            )
                        else:
                            return JsonResponse(
                                {'status': 'different_vendors',
                                 'message': 'Items already in cart'
                                 }
                            )
                    except:
                        chkCart = Cart.objects.create(user=request.user, products=prod, quantity=1)
                        return JsonResponse(
                            {'status': 'Success',
                             'message': 'Product added to the cart.',
                             'cart_counter': get_cart_counter(request),
                             'qty': chkCart.quantity,
                             'cart_amount': get_cart_amount(request)
                             }
                        )
            except:
                return JsonResponse({'status': 'Failed', 'message': 'This product does not exist.'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request.'})
    else:
        return JsonResponse({'status': 'login_required', 'message': 'Please login to continue.'})


def remove_from_cart(request, product_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Check if the product exists
            try:
                prod = Product.objects.get(id=product_id)
                # Check if the user has already added product in the cart
                try:
                    chkCart = Cart.objects.get(user=request.user, products=prod)
                    # Decrease the cart quantity
                    if chkCart.quantity > 1:
                        chkCart.quantity -= 1
                        chkCart.save()
                    else:
                        chkCart.delete()
                        chkCart.quantity = 0
                    return JsonResponse(
                        {'status': 'Success',
                         'cart_counter': get_cart_counter(request),
                         'qty': chkCart.quantity,
                         'cart_amount': get_cart_amount(request)
                         }
                    )
                except:
                    return JsonResponse({'status': 'Failed', 'message': 'You do not have this item in your cart!'})
            except:
                return JsonResponse({'status': 'Failed', 'message': 'This product does not exist.'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request.'})
    else:
        return JsonResponse({'status': 'login_required', 'message': 'Please login to continue.'})


def delete_from_cart(request, cart_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Check if cart item exists
            try:
                cart_item = Cart.objects.get(user=request.user, id=cart_id)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse(
                        {
                            'status': 'Success',
                            'message': 'Cart item has been deleted.',
                            'cart_counter': get_cart_counter(request),
                            'cart_amount': get_cart_amount(request)
                        }
                    )
            except:
                return JsonResponse({'status': 'Failed', 'message': 'Cart item does not exist.'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request.'})
    else:
        return JsonResponse({'status': 'login_required', 'message': 'Please login to continue.'})


def delete_cart(request):
    print('delete cart is called')
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Check if cart items exists
            try:
                cart_item = Cart.objects.filter(user=request.user)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse(
                        {
                            'status': 'Success',
                            'message': 'Cart has been deleted.',
                            'cart_counter': get_cart_counter(request),
                            'qty': 0
                        }
                    )
            except:
                return JsonResponse({'status': 'Failed', 'message': 'No items in cart.'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request.'})
    else:
        return JsonResponse({'status': 'login_required', 'message': 'Please login to continue.'})


@login_required(login_url='login')
def cart(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    context = {
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/cart.html', context)


def search(request):
    if not 'address' in request.GET:
        return redirect('marketplace')
    else:
        address = request.GET['address']
        latitude = request.GET['lat']
        longitude = request.GET['lng']
        radius = request.GET['radius']
        keyword = request.GET['keyword']

        # get vendor IDs that has the product the user is looking for
        fetch_vendor_by_products = Product.objects.filter(product_title__icontains=keyword,
                                                          is_available=True).values_list('vendor', flat=True)
        vendors = Vendor.objects.filter(Q(id__in=fetch_vendor_by_products) |
                                        Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True))

        if latitude and longitude and radius:
            pnt = GEOSGeometry(f"POINT({longitude} {latitude})")

            vendors = Vendor.objects.filter(Q(id__in=fetch_vendor_by_products) |
                                        Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True),
                                        user_profile__location__distance_lte=(pnt, D(km=radius))
                                        ).annotate(distance=Distance("user_profile__location", pnt)).order_by('distance')

            for v in vendors:
                v.kms = round(v.distance.km, 1)

        vendor_count = vendors.count()
        context = {
            'vendors': vendors,
            'vendor_count': vendor_count
        }

        return render(request, 'marketplace/listings.html', context)


@login_required(login_url='login')
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()

    if cart_count <= 0:
        return redirect('marketplace')

    user_profile = UserProfile.objects.get(user=request.user)
    default_values = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'phone': request.user.phone_number,
        'email': request.user.email,
        'address': user_profile.address,
        'country': user_profile.country,
        'state': user_profile.state,
        'city': user_profile.city,
        'pin_code': user_profile.pin_code
    }

    form = OrderForm(initial=default_values)
    context = {
        'form': form,
        'cart_items': cart_items
    }
    return render(request, 'marketplace/checkout.html', context)

