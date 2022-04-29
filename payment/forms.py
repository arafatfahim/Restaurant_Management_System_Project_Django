from dataclasses import fields
from turtle import mode
from django import forms
from .models import BillingAddress
from hotel.models import Order

class BillingAddressForm(forms.ModelForm):
    class Meta:
        model = BillingAddress
        fields =['first_name', 'last_name','address',
                 'country',  'city', 'zipcode', 'phone_number']


class PaymentMethodForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['payment_method']
