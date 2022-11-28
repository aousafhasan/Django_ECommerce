from django.db import models
import datetime
from datetime import date
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
# Create your models here.

# def validate_stock(value):
#     if value >= 1000:
#         raise ValidationError(
#             _('%(value)s is greater then 1000'),
#             params={'value': value},
#         )
#     elif value <=0:
#         raise ValidationError(
#             _('%(value)s is less then 0'),
#             params={'value': value},
#         )

class Category(models.Model):
    name = models.CharField(max_length=200)
    warehouse = models.CharField(max_length=20, default='Windsor')

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=100, validators=[MinValueValidator(0),MaxValueValidator(1000)])
    available = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    interested = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    def refill(self):
        self.stock = self.stock + 100
        return self.stock


class Client(User):
    PROVINCE_CHOICES = [
    ('AB', 'Alberta'),
    ('MB', 'Manitoba'),
    ('ON', 'Ontario'),
    ('QC', 'Quebec'),]
    company = models.CharField(max_length=50, blank=True)
    shipping_address = models.CharField(max_length=300, null=True, blank=True)
    city = models.CharField(max_length=20, default="Windsor")
    province=models.CharField(max_length=2, choices=PROVINCE_CHOICES, default='ON')
    interested_in = models.ManyToManyField(Category)
    clientImage = models.ImageField(upload_to='clientImages/', blank=True)

    def __str__(self):
        return self.first_name + ' ' + self.last_name

class Order(models.Model):
    product = models.ForeignKey(Product, related_name="orders",on_delete=models.CASCADE)
    client = models.ForeignKey(Client, related_name='orders', on_delete=models.CASCADE)
    num_units = models.PositiveIntegerField()
    ORDER_STAGES = [(0, 'Order Cancelled'), (1, 'Order Placed'), (2, 'Order Shipped'), (3, 'Order Delivered'), ]
    order_status = models.IntegerField(choices=ORDER_STAGES, default=1)
    status_date = models.DateField(default=date.today())

    def __str__(self):
        # return self.product._str() + '--' + self.client.str_()
        orderstatus = self.order_status
        return 'Date: ' + self.status_date.strftime("%x") + ', Status: ' + self.ORDER_STAGES[orderstatus][
            1] + ', Client: ' + self.client.first_name + ' ' + self.client.last_name + ' ,Product: ' + self.product.name


    def total_cost(self):
        return self.product.price * self.num_units