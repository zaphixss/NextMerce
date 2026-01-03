from . import views
from django.urls import path

urlpatterns = [
    
    path('customer/dashboard/', views.customer_dashboard,  name='customer_dashboard'),
    path('customer/orders/', views.customer_orders,  name='customer_orders'),
    path('customer/order/detail/<id>/', views.order_detail,  name='customer_order_detail'),
    path('customer/wishlist/', views.customer_wishlist,  name='customer_wishlist'),
    path('customer/wishlist/delete/<id>', views.customer_wishlist_delete,  name='customer_wishlist_delete'),
    path('customer/account/settings', views.customer_account_settings,  name='customer_settings'),
    path('customer/account/update', views.customer_profile_update,  name='customer_settings_update'),
    path('customer/account/reviews', views.customer_pending_review,  name='customer_reviews'),
    path('customer/account/review/detail/<id>/', views.customer_review_detail,  name='review_detail'),

]





