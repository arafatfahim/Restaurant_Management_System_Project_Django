from dataclasses import field
from django.db import models

# Create your models here.

from django.contrib.auth.models import User

class BillingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    zipcode = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s billingaddress"

    def is_fully_filled(self):
        field_names =[f.name for f in self._meta.get_field()]
        for field_name in field_names:
            value = getattr(self, field_name)
            if value is None or value == '' :
                return False
        return True