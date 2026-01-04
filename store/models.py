from django.db import models
from userauth import models as userauth_model
from django.utils.text import slugify
from django.db.models import Avg
from django.utils import timezone
# Create your models here.

class Product(models.Model):
    STATUS = (
        ("Published", "Published"),
        ("Draft", "Draft"),
        ("Disabled", "Disabled"),
    )

    BANNERS = (
        ("Banner 1", "Banner 1"),
        ("Banner 2", "Banner 2"),
        ("Banner 3", "Banner 3"),
        ("Banner 4", "Banner 4"),
        ("Banner 5", "Banner 5"),
        ("Banner 6", "Banner 6"),
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
    banner = models.CharField(max_length=50, choices=BANNERS, blank=True, null=True)

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
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    qty = models.IntegerField(default=0, null=True, blank=True)
    sub_total = models.DecimalField(default=0, decimal_places=2, max_digits=12, null=True, blank=True)

    def __str__(self):
        product_name = self.product.name if self.product else "Deleted product"
        user_name = getattr(self.user, "username", None) or getattr(self.user, "email", None) or "Unknown user"
        return f"{user_name} - {product_name}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "product"], name="unique_cart_user_product")
        ]

class Wishlist(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(userauth_model.User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        if self.product:
            return self.product.name
        return "Wishlist Item (No Product)"
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "product"], name="unique_wishlist_user_product")
        ]
    
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
    fullname = models.CharField(max_length=50, null=True, blank=True)
    mobile = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=100, default='Unknown City')
    address = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    total = models.DecimalField(default=0, decimal_places=2, max_digits=12, null=True, blank=True)
    payment_status = models.CharField(max_length=50, choices=STATUS, default="Pending")
    date = models.DateTimeField(default=timezone.now, null=True, blank=True)


    def order_items(self):
        return OrderItem.objects.filter(order=self)
    
    def __str__(self):
        return str(self.id)
    
class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    qty = models.IntegerField(default=0, null=True, blank=True)
    sub_total = models.DecimalField(default=0, decimal_places=2, max_digits=12, null=True, blank=True)
    reviewed = models.BooleanField(default=False, null=True)

    def __str__(self):
        if self.product:
            return self.product.name
        return f"OrderItem #{self.pk} (no product)"
    
class Reviews(models.Model):
    RATING_CHOICES = [
        (1, '★☆☆☆☆ (1/5)'),
        (2, '★★☆☆☆ (2/5)'),
        (3, '★★★☆☆ (3/5)'),
        (4, '★★★★☆ (4/5)'),
        (5, '★★★★★ (5/5)'),
    ]
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    image = models.ImageField(upload_to='image', null=True, blank=True)
    user = models.ForeignKey(userauth_model.User, on_delete=models.SET_NULL, null=True)
    order_item = models.OneToOneField(OrderItem, on_delete=models.CASCADE, related_name="review", null=True)
    name = models.CharField(max_length=50, null=True)
    review = models.TextField(null=True)
    rating = models.IntegerField(choices=RATING_CHOICES, default=None)
    date = models.DateTimeField(default=timezone.now, null=True, blank=True)
    reply = models.BooleanField(default=False, null=True)
    

    def __str__(self):
        if self.product:
            return self.product.name
        else:
            return "Review (No Product)"
        
class Contact_Message(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=15)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name