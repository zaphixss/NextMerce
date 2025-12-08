from django.urls import path
from store import views

urlpatterns = [
    path('',views.index, name='index'),
    path('product/detail/<slug>/',views.product_detail, name='product_detail'),
    path('category/detail/<id>/',views.category_detail, name='category_detail'),
    path('product/best/selling',views.best_selling, name='best_selling'),
    path('product/shop/',views.shop, name='shop'),
    path('add/cart/<id>/',views.add_to_cart, name='add_cart'),
    path('cart/', views.cart,  name='cart'),
    path('cart/delete/<id>', views.cart_delete,  name='cart_delete'),
    path('cart/update/<id>', views.cart_update,  name='cart_update'),
    path('customer/home', views.customer_home,  name='customer_home'),
    path('customer/orders', views.customer_orders,  name='customer_orders'),
    path('add/wishlist/<id>/',views.add_wishlist, name='add_wishlist'),
    path('wishlist',views.user_wishlist, name='wishlist'),
    path('wishlist/delete/<id>', views.wishlist_delete,  name='wishlist_delete'),

]