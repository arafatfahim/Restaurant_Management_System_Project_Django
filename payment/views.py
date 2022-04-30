from django.shortcuts import render
import json
from django.views.generic import TemplateView
# Create your views here.
from sslcommerz_python.payment import SSLCSession
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import payment
from .models import BillingAddress
from .forms import BillingAddressForm, PaymentMethodForm
from django.contrib.auth.models import User
from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect, HttpResponse
from hotel.models import Cart, Order, Customer
from django.utils import timezone
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse



class CheckoutTemplateView(TemplateView, LoginRequiredMixin):
    def get(self, request, *args, **kwargs):
        saved_address = BillingAddress.objects.get_or_create(user=request.user or None)
        saved_address = saved_address[0]
        form = BillingAddressForm(instance=saved_address)
        payment_method = PaymentMethodForm()
        user = User.objects.get(id=request.user.id)
        items = Cart.objects.filter(user=user)
        # pay_meth = request.GET.get('paymeth')
        total = 0
        for item in items:
            total += item.food.sale_price
        context = {
            'billing_address': form,
            'payment_method': payment_method,
            'items' : items,
            'total' : total

        }
        return render (request, 'checkout.html', context)

    def post(self, request, *args, **kwargs):
        # saved_address = BillingAddress.objects.get_or_create(user=request.user or None)
        # saved_address = saved_address[0]
        # form = BillingAddressForm(instance=saved_address)
        # payment_obj = Order.objects.filter(customer=request.user)
        # payment_form = PaymentMethodForm(instance=payment_obj)
        customer = Customer.objects.get(customer=request.user)
        print(customer)
        items = Cart.objects.filter(user=request.user)
        if request.method == 'post' or request.method == 'POST':
            # form = BillingAddressForm(request.POST, instance=saved_address)
            payment_method = request.POST['payment_method']
            # pay_form = PaymentMethodForm(request.POST, instance=payment_obj)

            if payment_method == 'Cash On Delivery':
                total = 0
                store_all = []
                price_all = []
                for item in items:
                    food = item.food
                    price = item.food.sale_price
                    total += item.food.sale_price
                    store_all.append(food)
                    data = ", \n".join(map(str, store_all))
                    price_all.append(price)
                    price_data = " \n".join(map(str, price_all))
                print(total)
                print(price_data)
                order = Order.objects.create(customer=customer, order_timestamp=timezone.now(), payment_status="Pending",
                                 delivery_status="Pending", payment_id='Cash On Delivery', food_items=data, food_price=price_data,  total_amount=total,
                                 payment_method="Cash On Delivery", location=customer.address)
                order.save()
                items.delete()      
                return redirect('hotel:thanks')

            if payment_method == 'Online Payment':
                store_id = settings.STORE_ID
                store_pass = settings.STORE_PASS
                mypayment = SSLCSession(sslc_is_sandbox=True, sslc_store_id=store_id, sslc_store_pass=store_pass)

                status_url = request.build_absolute_uri(reverse('payment:status'))
                mypayment.set_urls(success_url=status_url, fail_url=status_url, 
                                        cancel_url=status_url, ipn_url=status_url)

                total = 0
                data = []
                store_all = []
                for item in items:
                    food = item.food
                    total += item.food.sale_price
                    store_all.append(food)
                    data = ", \n".join(map(str, store_all))
                # print(total)
                # print(data)
                # print(customer)
                mypayment.set_product_integration(total_amount=Decimal(total), currency='BDT', product_category='food', product_name='data', num_of_item='item.quantity', shipping_method='YES', product_profile='None')

                mypayment.set_customer_info(name='customer', email='customer.user.email', address1='customer.address', address2='', city='Dhaka', postcode='1207', country='Bangladesh', phone=customer.contact)

                # billing_address = BillingAddress.objects.filter(user=request.user)[0]
                # print(billing_address.user.user)
                mypayment.set_shipping_info(shipping_to='customer', address='customer.address', city='dhaka', postcode='1207', country='Bangladesh')
                # If you want to post some additional values
                # mypayment.set_additional_values(value_a='cusotmer@email.com', value_b='portalcustomerid', value_c='1234', value_d='uuid')
                response_data = mypayment.init_payment()
                # print('==================')
                # print('==================')
                # print(response_data)
                # print('==================')
                # print('==================')


                return redirect(response_data['GatewayPageURL'])
            
            return redirect('checkout')


@csrf_exempt
def sslc_status(request):
    if request.method == 'post' or request.method == 'POST':
        payment_data = request.POST
        # print('==================')
        # print('==================')
        print(payment_data)
        status = payment_data['status']
        if status == 'VALID':
            val_id = payment_data['val_id']
            tran_id = payment_data['tran_id']
            card_issuer = payment_data['card_issuer']
            return HttpResponseRedirect(reverse('payment:sslc_complete', kwargs={'val_id':val_id, 'tran_id':tran_id, 'card_issuer':card_issuer}))
    return render(request, 'status.html')


@login_required
def sslc_complete(request, val_id, tran_id, card_issuer):
    # return HttpResponse(val_id)
    customer = Customer.objects.get(customer=request.user)
    print(customer.address)
    items = Cart.objects.filter(user=request.user)
    total = 0
    data = []
    store_all = []
    payment_id = tran_id
    payment_type = card_issuer
    print(payment_type)
    price_all = []
    for item in items:
        food = item.food
        price = item.food.sale_price
        total += item.food.sale_price
        store_all.append(food)
        data = ", \n".join(map(str, store_all))
        price_all.append(price)
        price_data = " \n".join(map(str, price_all))
    # print(total)
    # print(price_data)
    order = Order.objects.create(customer=customer, order_timestamp=timezone.now(), payment_status="Completed",
                        delivery_status="Pending", payment_id=payment_id, food_items=data, food_price=price_data,  total_amount=total,
                        payment_method="Online Payment", payment_type=payment_type, location=customer.address)
    order.save()
    items.delete()      
    return redirect('hotel:thanks')


