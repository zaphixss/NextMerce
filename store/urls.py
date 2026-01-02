from django.urls import path
from store import views

urlpatterns = [
    path('',views.index, name='index'),
    path('product/detail/<slug>/',views.product_detail, name='product_detail'),
    path('category/detail/<id>/',views.category_detail, name='category_detail'),
    path('product/search/', views.search_view, name='search_view'),
    path('product/best/selling',views.best_selling, name='best_selling'),
    path('product/shop/',views.shop, name='shop'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('faq/', views.faq_view, name='faq'),
    path('policy/', views.policy_view, name='policy'),
    path("cart/add/<id>/", views.add_to_cart, name="add_cart"),
    path('cart/', views.cart,  name='cart'),
    path('cart/delete/<id>', views.cart_delete,  name='cart_delete'),
    path('cart/update/<id>', views.cart_update,  name='cart_update'),
    path('customer/orders', views.customer_orders,  name='customer_orders'),
    path("wishlist/toggle/<id>/", views.add_wishlist, name="add_wishlist"),
    path('wishlist',views.user_wishlist, name='wishlist'),
    path('wishlist/delete/<id>', views.wishlist_delete,  name='wishlist_delete'),
    path('checkout/<id>/',views.checkout_view, name='checkout'),
    path('create_checkout_view',views.create_checkout_view, name='create_checkout_view'),
    path("api/paystack/verify/", views.verify_payment, name="verify_payment"),
    path("checkout/payment/status/<id>/", views.payment_success, name="payment_success"),
   
]