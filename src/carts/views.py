from django.shortcuts import render, redirect

from .models import Cart
from products.models import Product
from orders.models import Order
from billing.models import BillingProfile
from accounts.models import GuestEmail
from addresses.models import Address

from accounts.forms import LoginForm, GuestForm
from addresses.forms import AddressForm

# Create your views here.

def cart_home(request):
  cart_obj, new_obj = Cart.objects.new_or_get(request)
  context = {
    'cart' : cart_obj
  }
  return render(request, 'carts/home.html', context)


def cart_update(request):
  product_id = request.POST.get('product_id')
  if product_id is not None:
    try:
      product_obj = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
      return redirect('cart:home')  
    cart_obj, new_obj = Cart.objects.new_or_get(request)
    if product_obj in cart_obj.products.all():
      cart_obj.products.remove(product_obj)
    else:
      cart_obj.products.add(product_obj)
    request.session['cart_items'] = cart_obj.products.count()
  # return  redirect(product_obj.get_absolute_url())
  return redirect('cart:home')

def checkout_home(request):
  cart_obj, cart_created = Cart.objects.new_or_get(request)
  order_obj = None
  if cart_created or cart_obj.products.count() == 0:
    return redirect('cart:home')
  login_form = LoginForm()
  guest_form = GuestForm()
  address_form = AddressForm()
  shipping_address_id = request.session.get('shipping_address_id', None)
  billing_address_id = request.session.get('billing_address_id', None)
  billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
  
  if billing_profile is not None:
    order_obj, order_obj_created = Order.objects.new_or_get(billing_profile, cart_obj)
    if shipping_address_id:
      order_obj.shipping_address = Address.objects.get(id=shipping_address_id)
      del request.session['shipping_address_id']
    if billing_address_id:
      order_obj.billing_address = Address.objects.get(id=billing_address_id)
      del request.session['billing_address_id']
    if shipping_address_id or billing_address_id:
      order_obj.save()
  context = {
    'object': order_obj,
    'billing_profile': billing_profile,
    'login_form': login_form,
    'guest_form': guest_form,
    'address_form': address_form,
  }
  return render(request, 'carts/checkout.html', context)