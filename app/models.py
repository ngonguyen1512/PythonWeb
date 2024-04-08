from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.
class State(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=True, blank=False)
    def __str__(self):
        return self.name

class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=True, blank=False)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return self.name

class Color(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=255, null=True, blank=False)
    name = models.CharField(max_length=255, null=True, blank=False)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return self.code

class Size(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=255, null=True, blank=False)
    name = models.CharField(max_length=255, null=True, blank=False)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return self.code

class Sample(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=True, blank=False)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=False)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=False)
    def __str__(self):
        return self.name

class Product(models.Model):
    id = models.AutoField(primary_key=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=False)
    sample = models.ForeignKey(Sample, on_delete=models.SET_NULL, null=True, blank=False)
    image = models.ImageField(null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=False)
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=False)
    discount = models.IntegerField(null=True, blank=True)
    price = models.IntegerField(null=True, blank=True)
    infor = models.CharField(max_length=255, null=True, blank=True)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=False)
    def __str__(self):
        return self.name
    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url

class Like(models.Model):
    id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=False)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=False)
    def __str__(self):
        return self.customer.username

class Quantity(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=False)
    size = models.ForeignKey(Size, on_delete=models.SET_NULL, null=True, blank=False)
    quantity = models.IntegerField(null=True, blank=False, default=0)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=False)
    def __str__(self):
        return str(self.product)

class Order(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateTimeField(default=timezone.now)
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=False, related_name='orders_accounted')
    phone = models.IntegerField(null=True, blank=False)
    address = models.CharField(max_length=255, null=True, blank=False)
    fee = models.IntegerField(null=True, blank=False)
    total = models.IntegerField(null=True, blank=False)
    accept = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders_accepted')
    shipper = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders_shipper')
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True)
    explanation = models.CharField(max_length=255, null=False, blank=True)
    def __str__(self):
        return str(self.id)

class OrderDetail(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True)
    size = models.ForeignKey(Size, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    price = models.IntegerField(null=True, blank=True)
    discount = models.IntegerField(null=True, blank=True)
    amount = models.IntegerField(null=True, blank=True)

class Cart(models.Model):
    id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=False)
    def __str__(self):
        return str(self.id)

class CartDetail(models.Model):
    id = models.AutoField(primary_key=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True, blank=False, related_name='cart_details')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    size = models.ForeignKey(Size, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
