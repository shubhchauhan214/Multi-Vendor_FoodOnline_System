from marketplace.models import Cart, Tax
from menu.models import Product


def get_cart_counter(request):
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart_items = Cart.objects.filter(user=request.user)
            if cart_items:
                for cart_item in cart_items:
                    cart_count += cart_item.quantity
            else:
                cart_count = 0
        except:
            cart_count = 0
    return dict(cart_count=cart_count)


def get_cart_amount(request):
    subtotal = 0
    pickup_fee = 10
    tax = 0
    grand_total = 0
    tax_dict = {}
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            product = Product.objects.get(pk=item.products.id)
            subtotal += (product.price * item.quantity)
            subtotal = round(subtotal, 2)

        get_taxes = Tax.objects.filter(is_active=True)
        for tax_val in get_taxes:
            tax_type = tax_val.tax_type
            tax_percentage = tax_val.tax_percentage
            tax_amount = round((tax_percentage * (subtotal + pickup_fee)) / 100, 2)
            tax_dict.update({tax_type: {str(tax_percentage): tax_amount}})

        for key in tax_dict.values():
            for x in key.values():
                tax = tax + x

        # {'CGST': {'9.00': '2.00'}, 'SGST': {'7.00': '1.56'}}
        # tax = round(float(0.13) * float(subtotal + pickup_fee), 2)
        grand_total = round(float(subtotal) + float(pickup_fee) + float(tax), 2)
    return dict(subtotal=subtotal, pickup_fee=pickup_fee, tax=tax, grand_total=grand_total, tax_dict=tax_dict)
