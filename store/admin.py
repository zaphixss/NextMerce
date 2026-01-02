from django.contrib import admin
from store import models

# Register your models here.

class OrderItemInline(admin.StackedInline):
    model = models.OrderItem

class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "fullname"]
    inlines = [OrderItemInline]

admin.site.register(models.Product)
admin.site.register(models.Category)
admin.site.register(models.Cart)
admin.site.register(models.Reviews)
admin.site.register(models.Wishlist)
admin.site.register(models.Product_Image)
admin.site.register(models.Order, OrderAdmin)
admin.site.register(models.OrderItem)
