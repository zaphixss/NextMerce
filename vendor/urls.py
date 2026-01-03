from django.urls import path
from vendor import views

urlpatterns = [
    path('dashboard/',views.vendor_dashboard, name='vendor_dashboard'),
    path('dashboard/products/', views.vendor_product_list, name='vendor_product_list'),
    path('dashboard/products/add/', views.vendor_create_product, name='vendor_create_product'),
    path('ajax/check-product-name/', views.ajax_check_product_name, name='ajax_check_product_name'),
    path('dashboard/products/edit/<id>/', views.vendor_edit_product, name='vendor_edit_product'),
    path('dashboard/products/delete/<id>/', views.product_delete, name='vendor_delete_product'),
    path('dashboard/orders/', views.vendor_orders, name='vendor_orders'),
    path('dashboard/order/detail/<id>/', views.vendor_order_detail, name='order_detail'),
    path('dashboard/order/delete/<id>/', views.vendor_order_delete, name='vendor_order_delete'),
    path('dashboard/customers/', views.vendor_customers, name='vendor_customers'),
    path('dashboard/reviews/', views.vendor_reviews, name='vendor_reviews'),
    path('dashboard/profile/', views.vendor_profile, name='vendor_profile'),

]