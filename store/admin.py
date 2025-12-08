from django.contrib import admin
from store import models

# Register your models here.

admin.site.register(models.Product)
admin.site.register(models.Category)
admin.site.register(models.Cart)
admin.site.register(models.Reviews)
admin.site.register(models.Wishlist)
admin.site.register(models.Product_Image)
