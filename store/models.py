from django.db import models
from userauth import models as userauth_model
from django.utils.text import slugify
# Create your models here.

class Product(models.Model):
    STATUS = (
        ("Published", "Published"),
        ("Draft", "Draft"),
        ("Disabled", "Disabled"),
    )

    status = models.CharField(max_length=500, choices=STATUS, default="Published")
    user = models.ForeignKey(userauth_model.User, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey("store.Category",on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    additional_information = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='image', null=True, blank=True)
    sale_price = models.DecimalField(default=0, decimal_places=2, max_digits=12)
    regular_price = models.DecimalField(default=0, decimal_places=2, max_digits=12, null=True, blank=True)
    in_stock = models.BooleanField(default=False)
    free_delivery = models.BooleanField(default=False)
    qty = models.IntegerField(default=0, null=True, blank=True)
    featured = models.BooleanField(default=False)
    popular = models.BooleanField(default=False)
    slug = models.SlugField(unique=True, blank=True, null=True)
    cover_image = models.ImageField(upload_to='image', null=True, blank=True)
    best_selling = models.BooleanField(default=False)
    new_arrivals = models.BooleanField(default=False)


    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Category(models.Model):
    title = models.CharField(max_length=50)
    image = models.ImageField(upload_to='image', null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True, null=True)

    def __str__(self):
        return self.title

class Cart(models.Model):
    user = models.ForeignKey(userauth_model.User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    qty = models.IntegerField(default=0, null=True, blank=True)
    sub_total = models.DecimalField(default=0, decimal_places=2, max_digits=12, null=True, blank=True)

    def __str__(self):
        return self.product.name
    
class Reviews(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    image = models.ImageField(upload_to='image', null=True, blank=True)
    user = models.ForeignKey(userauth_model.User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.product

class Wishlist(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(userauth_model.User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.product
    
class Product_Image(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    image = models.ImageField(upload_to='image', null=True, blank=True)

    def __str__(self):
        return self.product



class Order(models.Model):
    STATUS = (
        ("Paid", "Paid"),
        ("Pending", "Pending"),
        ("Failed", "Failed"),
    )

    user = models.ForeignKey(userauth_model.User, on_delete=models.SET_NULL, null=True)
    total = models.DecimalField(default=0, decimal_places=2, max_digits=12, null=True, blank=True)
    payment_status = models.CharField(max_length=50, choices=STATUS, default="Pending")
    

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    qty = models.IntegerField(default=0, null=True, blank=True)
    sub_total = models.DecimalField(default=0, decimal_places=2, max_digits=12, null=True, blank=True)

    def __str__(self):
        return self.product.name
