from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import datetime


class Customer(models.Model):
    pending = 'Pending'
    verified = 'Verified'

    STATUS = (
        (pending, pending),
        (verified, verified),
    )

    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.TextField()
    referal_code = models.CharField(max_length=10)
    contact = models.CharField(max_length=10)
    orders = models.IntegerField(default=0)
    total_sale = models.IntegerField(default=0)
    status = models.CharField(max_length=50, choices=STATUS)

    def __str__(self):
        return self.customer.first_name + " " + self.customer.last_name


class Staff(models.Model):
    weiter = 'weiter'
    deliveryboy = 'Delivery Boy'
    chef = 'Chef'

    ROLES = (
        (weiter, weiter),
        (chef, chef),
        (deliveryboy, deliveryboy),
    )

    staff_name = models.CharField(max_length=255)
    address = models.TextField()
    contact = models.CharField(max_length=10)
    email = models.EmailField(max_length=255)
    salary = models.IntegerField()
    role = models.CharField(max_length=30, choices=ROLES)

    def __str__(self):
        return self.staff_name


class Food(models.Model):
    bengali = 'Bengali'
    thai = 'Thai'
    chinese = 'Chinese'
    indian = 'Indian'
    italian = 'Italian'

    COURSE = (
        (bengali, bengali),
        (thai, thai),
        (chinese, chinese),
        (indian, indian),
        (italian, italian),
    )

    disabled = 'Disabled'
    enabled = 'Enabled'

    STATUS = (
        (disabled, disabled),
        (enabled, enabled),
    )

    name = models.CharField(max_length=250)
    course = models.CharField(max_length=50, choices=COURSE)
    # status = models.CharField(max_length=50, choices=STATUS)
    content_description = models.TextField()
    ingradients = models.TextField()
    base_price = models.FloatField()
    sale_price = models.FloatField(default=base_price)
    discount = models.DecimalField(default=0, decimal_places=2, max_digits=5)
    image = models.FileField(blank=True, null=True)
    num_order = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    # def calculateSalePrice(self):
    #   self.sale_price = (100.0 - self.discount)/100.0 * self.base_price


class Cart(models.Model):
    quantity = models.IntegerField(default=1)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    # price = models.ForeignKey(Food, on_delete=models.CASCADE, related_name='FoodPrice')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.food.__str__()


class Order(models.Model):
    pending = 'Pending'
    completed = 'Completed'

    STATUS = (
        (pending, pending),
        (completed, completed),
    )

    PAYMENT = (
        ('Cash On Delivery', 'Cash On Delivery'),
        ('Online Payment', 'Online Payment'),
    )

    pickup = 'PickUp'
    delivery = 'Delivery'

    TYPE = (
        (pickup, pickup),
        (delivery, delivery),
    )

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_timestamp = models.DateTimeField(auto_now_add=True)
    delivery_timestamp = models.DateTimeField(auto_now=True)
    # food_items = models.ForeignKey(Food, on_delete=models.CASCADE)
    order_items = models.ManyToManyField(Cart)
    food_items = models.TextField(null=True)
    food_price = models.TextField(null=True)
    payment_id = models.CharField(max_length=264, blank=True, null=True)
    payment_status = models.CharField(max_length=100, choices=STATUS)
    delivery_status = models.CharField(max_length=100, choices=STATUS)
    if_cancelled = models.BooleanField(default=False)
    cancelled_reason = models.TextField(blank=True, null=True)
    refund_request = models.BooleanField(default=False)
    total_amount = models.IntegerField(blank=True, null=True)
    payment_method = models.CharField(max_length=100, choices=PAYMENT, default='Cash On Delivery')
    payment_type = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    delivery_boy = models.ForeignKey(Staff, on_delete=models.CASCADE, null=True, blank=True)

    def confirmOrder(self):
        self.order_timestamp = timezone.localtime().__str__()[:19]
        self.payment_status = self.completed
        self.save()

    def confirmDelivery(self):
        self.delivery_timestamp = timezone.localtime().__str__()[:19]
        self.delivery_status = self.completed
        self.save()

    def __str__(self):
        return self.customer.__str__()


class Comment(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    content = models.CharField(max_length=250)


class Data(models.Model):
    date = models.DateField()
    sales = models.IntegerField()
    expenses = models.IntegerField()


class OrderContent(models.Model):
    quantity = models.IntegerField(default=1)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)


class DeliveryBoy(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    delivery_boy = models.ForeignKey(Staff, on_delete=models.CASCADE)


class UserOrder(models.Model):
    Customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    food_items = models.ForeignKey(Order, on_delete=models.CASCADE)
    total_price = models.IntegerField()


