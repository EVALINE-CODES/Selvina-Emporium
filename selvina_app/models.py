from django.db import models
from django_resized import ResizedImageField
from django.contrib.auth.models import User
from solo.models import SingletonModel


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200, null=True)
    description = models.CharField(max_length=550, null=True)
    digital = models.BooleanField(default=False, null=True, blank=True)
    price = models.FloatField(max_length=200, null=True)
    image = ResizedImageField(
        size=[300, 300], upload_to="products/", null=True, blank=True
    )
    rating = models.FloatField(default=0)

    def __str__(self):
        if self.name:
            return self.name
        return "Unnamed Product"

    class Meta:
        ordering = ["id"]

    @property
    def stars(self):
        return range(int(self.rating))

    @property
    def empty_stars(self):
        return range(5 - int(self.rating))


class Order(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True
    )
    date_order = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False, null=True, blank=True)
    transaction_id = models.CharField(max_length=200, null=True)

    def __str__(self):
        return str(self.id)

    @property
    def shipping(self):
        shipping = False
        orderitems = self.orderitem_set.all()
        for i in orderitems:
            if i.product.digital == False:
                shipping = True
        return shipping

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total


class ShippingAddress(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True
    )
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)
    zipcode = models.CharField(max_length=200, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address


class Wishlist(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        customer_name = self.customer.name if self.customer else "Unknown Customer"
        product_name = self.product.name if self.product else "Unknown Product"
        return f"{customer_name} - {product_name}"


class URLConfiguration(SingletonModel):
    phone = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(max_length=150, null=True, blank=True)
    location = models.CharField(max_length=500, null=True, blank=True)
    about_us = models.TextField(null=True, blank=True)
    about_us_img = models.ImageField(upload_to="images/", null=True, blank=True)
    maintenance_mode = models.BooleanField(default=False)

    def __str__(self):
        return " URLConfiguration"

    class Meta:
        verbose_name = "URLConfiguration"


class ContactMessage(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.CharField(max_length=100)
    subject = models.CharField(max_length=1000)
    message = models.TextField()

    def __str__(self):
        return self.subject
