from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from store.models import OrderItem, Order, Product, Reviews, Category
from django.db.models import Avg, Sum, Q, Count
from django.db.models.functions import TruncMonth
import json
from django.contrib import messages
from django.utils.text import slugify
from django.core.paginator import Paginator
from django.http import JsonResponse

@login_required
def vendor_dashboard(request):
    user = request.user
    
    orders_count = OrderItem.objects.filter(product__user=user, order__payment_status='Paid')
    active_products = Product.objects.filter(status='Published', user=user)
    
    rating_data = Reviews.objects.filter(product__user=user).aggregate(Avg('rating'))
    avg_rating = rating_data['rating__avg']
    avg_rating = round(avg_rating, 1) if avg_rating else 0

    revenue_data = OrderItem.objects.filter(order__payment_status='Paid', product__user=user).aggregate(Sum("sub_total"))    
    revenue = revenue_data['sub_total__sum'] or 0 # Handle None if no sales
    
    orders = (
        Order.objects
        .filter(orderitem__product__user=user)
        .annotate(
            vendor_total=Sum(
                "orderitem__sub_total", 
                filter=Q(orderitem__product__user=user)
            )
        )
        .order_by('-date') 
    )


    # --- NEW: CHART DATA CALCULATIONS ---

    # 1. REVENUE CHART (Area Chart)
    # Group OrderItems by Month and Sum the sub_total
    monthly_revenue = (
        OrderItem.objects
        .filter(product__user=user, order__payment_status='Paid')
        .annotate(month=TruncMonth('order__date')) # Make sure 'date' is the correct field name on OrderItem (or order__date)
        .values('month')
        .annotate(total_revenue=Sum('sub_total'))
        .order_by('month')
    )

    # Prepare lists for ApexCharts
    revenue_dates = []
    revenue_amounts = []

    for item in monthly_revenue:
        # Convert date to string (e.g., "Jan")
        revenue_dates.append(item['month'].strftime('%b')) 
        # Convert Decimal to float for JSON
        revenue_amounts.append(float(item['total_revenue']))


    # 2. CATEGORY CHART (Donut Chart)
    # Group OrderItems by Product Category and Sum sub_total (or Count)
    # NOTE: Adjust 'product__category__title' to match your actual Category model field name (e.g. name, title)
    category_sales = (
        OrderItem.objects
        .filter(product__user=user, order__payment_status='Paid')
        .values('product__category__title') 
        .annotate(total_sales=Sum('sub_total'))
        .order_by('-total_sales') # Sort biggest first
    )

    category_labels = []
    category_data = []

    for item in category_sales:
        category_labels.append(item['product__category__title'])
        category_data.append(float(item['total_sales']))


    context = {
        'orders_count': orders_count,
        'active_products': active_products,
        'avg_rating': avg_rating,
        'revenue': revenue,
        'orders': orders,
        
        # Pass JSON strings to template
        'revenue_dates': json.dumps(revenue_dates),
        'revenue_amounts': json.dumps(revenue_amounts),
        'category_labels': json.dumps(category_labels),
        'category_data': json.dumps(category_data),
    }
    return render(request, 'vendor/dashboard.html', context)

@login_required
def vendor_product_list(request):
    all_products = Product.objects.filter(user=request.user).order_by("-id")
    
    pub_list = all_products.filter(status="Published")
    draft_list = all_products.filter(status="Draft")
    dis_list = all_products.filter(status="Disabled")
    
   
    pub_paginator = Paginator(pub_list, 8)
    draft_paginator = Paginator(draft_list, 8)
    dis_paginator = Paginator(dis_list, 8)

    published_products = pub_paginator.get_page(request.GET.get('pub_page'))
    draft_products = draft_paginator.get_page(request.GET.get('draft_page'))
    disabled_products = dis_paginator.get_page(request.GET.get('dis_page'))

    average_price = all_products.aggregate(avg_price=Avg('sale_price'))['avg_price'] or 0
    formatted_avg = "{:,.0f}".format(round(average_price))
    context = {
        'products': all_products,
        'published_products': published_products,
        'draft_products': draft_products,
        'disabled_products': disabled_products,
        'average_price': formatted_avg,
        'pub_list': pub_list,
        'draft_list': draft_list,
        'dis_list': dis_list,
    }
    return render(request, 'vendor/product_list.html', context)

def ajax_check_product_name(request):
    name = request.GET.get('name', None)
    exists = Product.objects.filter(user=request.user, name__iexact=name).exists()
    return JsonResponse({'exists': exists})

@login_required
def vendor_create_product(request):
    categories = Category.objects.all()
    status_choices = Product.STATUS 

    if request.method == "POST":
        name = request.POST.get('name')
        description = request.POST.get('description')
        additional_info = request.POST.get('additional_info')
        regular_price = request.POST.get('regular_price') 
        sale_price = request.POST.get('sale_price') 
        qty = request.POST.get('qty') 
        status = request.POST.get('status') 
        category_id = request.POST.get('category')
        
        # Booleans
        free_delivery = 'free_delivery' in request.POST
        in_stock = 'in_stock' in request.POST
        new_arrivals = 'new_arrivals' in request.POST
        
        # Files
        image = request.FILES.get('image')
        cover_image = request.FILES.get('cover_image')
        
        
        if not image:
            messages.error(request, "Please add a product image before publishing!")
            return render(request, 'vendor/add_product.html', {
                "categories": categories,
                "status": status_choices
            })

        category = Category.objects.get(id=category_id) if category_id else None

        new_product = Product.objects.create(
            user=request.user,                
            category=category,                
            name=name,
            slug=slugify(name),               
            description=description,
            additional_information=additional_info,
            regular_price=regular_price,
            sale_price=sale_price,
            qty=qty,
            status=status,
            in_stock=in_stock,
            free_delivery=free_delivery,
            image=image,                      
            cover_image=cover_image,   
            new_arrivals=new_arrivals,
        )

        messages.success(request, f"Product '{name}' created successfully!")
        return redirect('vendor_product_list')

    context = {
        "categories": categories,
        "status": status_choices 
    }
    
    return render(request, "vendor/add_product.html", context)

@login_required
def vendor_edit_product(request, id):
    product = Product.objects.get(id=id, user=request.user)
    categories = Category.objects.all()
    status_choices = Product.STATUS # Match status choices from Create View

    if request.method == "POST":
        name = request.POST.get('name')
        description = request.POST.get('description')
        additional_info = request.POST.get('additional_info') # Added
        
        regular_price = request.POST.get('regular_price') 
        sale_price = request.POST.get('sale_price') 
        qty = request.POST.get('qty') 
        
        status = request.POST.get('status') 
        category_id = request.POST.get('category')
        
        
        in_stock = 'in_stock' in request.POST
        free_delivery = 'free_delivery' in request.POST
        new_arrivals = 'new_arrivals' in request.POST 
        
        image = request.FILES.get('image')
        if image:
            product.image = image

        cover_image = request.FILES.get("cover_image")
        if cover_image:
            product.cover_image = cover_image

        product.name = name
        product.slug = slugify(name)
        product.description = description
        product.additional_information = additional_info 
        product.regular_price = regular_price
        product.sale_price = sale_price
        product.qty = qty
        product.status = status
        product.in_stock = in_stock
        product.free_delivery = free_delivery
        product.new_arrivals = new_arrivals 
        
        if category_id:
            product.category = Category.objects.get(id=category_id)

        product.save()
        messages.success(request, f"Updated {product.name} successfully!")
        return redirect("vendor_product_list")

    context = {
        "product": product,
        "categories": categories,
        "status": status_choices, # Pass status choices for the dropdown loop
    }
    return render(request, "vendor/edit_product.html", context)


def product_delete(request, id):
    product = Product.objects.get(id=id, user=request.user)
    product.delete()
    messages.success(request, f"Deleted {product.name} successfully!")
    return redirect("vendor_product_list")

@login_required
def vendor_orders(request):
    orders = (
        Order.objects
        .filter(orderitem__product__user=request.user)
        .annotate(
            vendor_total=Sum(
                "orderitem__sub_total", 
                filter=Q(orderitem__product__user=request.user)
            )
        )
        .order_by('-date') 
    )
    
    # Categorize for the dashboard tabs
    pending_orders = orders.filter(payment_status="pending")
    paid_orders = orders.filter(payment_status="paid")
    cancelled_orders = orders.filter(payment_status="cancelled")

    context = {
        'orders': orders,
        'pending_orders': pending_orders,
        'paid_orders': paid_orders,
        'cancelled_orders': cancelled_orders,
    }
    return render(request, 'vendor/orders.html', context)

def vendor_order_delete(request, id):
    order = Order.objects.get(id=id)
    
    order.delete()
    
    messages.success(request, "Order deleted successfully!")
    
    previous_url = request.META.get('HTTP_REFERER' )
    
    return redirect(previous_url)

@login_required
def vendor_order_detail(request, id):
    order = Order.objects.get(id=id)
    order_items = OrderItem.objects.filter(order=order, product__user=request.user)
    
    vendor_order_total = order_items.aggregate(total=Sum('sub_total'))['total'] or 0

    context = {
        'order': order,
        'order_items': order_items,
        'vendor_total': vendor_order_total, # Make sure the name matches your calculation
    }
    return render(request, 'vendor/order_detail.html', context)

@login_required
def vendor_customers(request):
    # Add a filter to ensure only completed, named orders are shown
    vendor_items = OrderItem.objects.filter(
        product__user=request.user, 
        order__fullname__isnull=False
    ).exclude(order__fullname="")
    
    customers = vendor_items.values(
        'order__id',  
        'order__user__id', 
        'order__fullname', 
        'order__mobile'
    ).annotate(
        total_items=Sum('qty'),
        order_count=Count('order', distinct=True)
    ).order_by('-total_items')

    context = {'customers': customers}
    return render(request, 'vendor/customers.html', context)

@login_required
def vendor_reviews(request):
    # Fetch all reviews for this vendor's products
    reviews = Reviews.objects.filter(
        product__user=request.user, 
        reply=False
    ).order_by("-date") 
    
    # Calculate Average Rating
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    if request.method == "POST":
        review_id = request.POST.get("review_id")
        reply_text = request.POST.get("reply")
        
        review = Reviews.objects.get( id=review_id, product__user=request.user)
        review.reply = reply_text
        review.reply = True
        review.save()
        
        messages.success(request, "Reply sent successfully!")
        return redirect("vendor_reviews")

    context = {
        'reviews': reviews,
        'average_rating': round(average_rating, 1),
    }
    return render(request, 'vendor/reviews.html', context)

@login_required
def vendor_profile(request):
    user = request.user  # your custom user model instance

    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        firstname = request.POST.get("firstname", "").strip()
        lastname = request.POST.get("lastname", "").strip()
        country = request.POST.get("country", "").strip()
        phone = request.POST.get("phone", "").strip()
        image = request.FILES.get("image")

        # ✅ Basic validation (email required)
        if not email:
            messages.error(request, "Email is required.")
            return redirect("profile_update")

        # ✅ Uniqueness checks (avoid crashing on unique constraint)
        if email != user.email and user.__class__.objects.filter(email=email).exists():
            messages.error(request, "That email is already in use.")
            return redirect("profile_update")


        # ✅ Update fields
        user.email = email
        user.firstname = firstname or None
        user.lastname = lastname or None
        user.country = country or None
        user.phone = phone or None

        # ✅ Update image only if user picked one
        if image:
            user.image = image

        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("vendor_profile")
    return render(request, 'vendor/profile.html')