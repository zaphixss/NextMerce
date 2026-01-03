from django.shortcuts import render, redirect, get_object_or_404
from .models import Category,Product, Cart, Wishlist, Order, OrderItem, Reviews
from django.contrib import messages
from decimal import Decimal
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction, IntegrityError
import json
import requests
from django.conf import settings
from django.http import JsonResponse


# Create your views here.
def index(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    featured_products = Product.objects.filter(featured=True)
    best_selling = Product.objects.filter(best_selling=True)
    new_arrivals = Product.objects.filter(new_arrivals=True)
    banner1 = Product.objects.filter(banner="Banner 1").first()
    banner2 = Product.objects.filter(banner="Banner 2").first() 
    banner3 = Product.objects.filter(banner="Banner 3").first()
    banner4 = Product.objects.filter(banner="Banner 4").first()
    context ={
        'categories':categories,
        'products':products,
        'featured_products':featured_products,
        'best_selling':best_selling,
        'new_arrivals':new_arrivals,
        'banner1':banner1,
        'banner2':banner2,
        'banner3':banner3,
        'banner4':banner4,
    }
    return render(request, 'index.html', context)

def product_detail(request, slug):
    product = Product.objects.get(slug=slug)
    products = Product.objects.all()
    reviews = Reviews.objects.filter(product=product)

    context = {
        'product': product,
        'products':products,
        'reviews':reviews
    }
    return render(request,'product_detail.html', context)

def category_detail(request, id):
    category = Category.objects.get(id=id)
    products = Product.objects.filter(category=category)

    context = {
        'products': products,
        'category':category
    }
    return render(request,'category_detail.html', context)

def best_selling(request):
    products = Product.objects.filter(best_selling=True).order_by('-id')

    paginator = Paginator(products, 8) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


    context ={
        'products': page_obj,
        'product':products
    }
    return render(request, 'best_selling.html', context)

def shop(request):
    products = Product.objects.filter(new_arrivals=True).order_by('id')
    categories = Category.objects.all()

    selected_categories = request.GET.getlist("category")

    if selected_categories:
        products = products.filter(category_id__in=selected_categories)

    paginator = Paginator(products, 6) 
    
    page_number = request.GET.get('page')
    
    page_obj = paginator.get_page(page_number)

    context = {
        'products': page_obj,
        'categories': categories,
        'selected_categories': selected_categories, 
        'product': products, 
    } 
    return render(request, 'shop.html', context)

def about_view(request):
    return render(request, 'pages/about.html')

def contact_view(request):
    return render(request, 'pages/contact.html')

def faq_view(request):
    return render(request, 'pages/FAQ.html')

def policy_view(request):
    return render(request, 'pages/policy.html')

@login_required
def user_wishlist(request):
    wishlist = Wishlist.objects.filter(user=request.user)
    context ={
        'wishlist': wishlist
    }
    return render(request, 'wishlist.html', context)

def wishlist_delete(request, id):
    wishlist = Wishlist.objects.get(id=id)
    wishlist.delete()
    return redirect('wishlist')

def is_ajax(request):
    return request.headers.get("x-requested-with") == "XMLHttpRequest"

@login_required
@require_POST
def add_to_cart(request, id):
    product = get_object_or_404(Product, id=id)
    qty = int(request.POST.get("qty", 1) or 1)

    if qty > product.qty:
        msg = "Qty exceed"
        if is_ajax(request):
            return JsonResponse({"ok": False, "message": msg}, status=400)
        messages.warning(request, msg)
        return redirect(request.META.get("HTTP_REFERER", "/"))

    try:
        with transaction.atomic():
            item, created = Cart.objects.get_or_create(
                user=request.user,
                product=product,
                defaults={"qty": 0, "sub_total": Decimal("0.00")},
            )
    except IntegrityError:
        item = Cart.objects.get(user=request.user, product=product)
        created = False

    item.qty += qty
    item.sub_total = item.qty * product.sale_price
    item.save()

    cart_count = Cart.objects.filter(user=request.user).count()

    if is_ajax(request):
        return JsonResponse({
            "ok": True,
            "message": "Added to cart ✅",
            "cartCount": cart_count,
            "itemQty": item.qty,
            "itemSubTotal": str(item.sub_total),
        })

    messages.success(request, "Added to cart ✅")
    return redirect(request.META.get("HTTP_REFERER", "/"))

@login_required
@require_POST
def add_wishlist(request, id):
    product = get_object_or_404(Product, id=id)

    deleted, _ = Wishlist.objects.filter(user=request.user, product=product).delete()
    if deleted:
        in_wishlist = False
        msg = "Removed from wishlist"
    else:
        try:
            with transaction.atomic():
                Wishlist.objects.create(user=request.user, product=product)
            in_wishlist = True
            msg = "Added to wishlist ❤️"
        except IntegrityError:
            in_wishlist = True
            msg = "Already in wishlist ❤️"

    wishlist_count = Wishlist.objects.filter(user=request.user).count()

    if is_ajax(request):
        return JsonResponse({
            "ok": True,
            "message": msg,
            "inWishlist": in_wishlist,
            "wishlistCount": wishlist_count,
        })

    messages.success(request, msg)
    return redirect(request.META.get("HTTP_REFERER", "/"))

@login_required
def cart(request):
    cart = Cart.objects.filter(user=request.user)
    total = Cart.objects.filter(user=request.user).aggregate(total=Sum('sub_total'))['total']
    print(total)
    context={
        'cart':cart,
        'total':total,
    }
    return render(request,'cart.html', context)

def cart_delete(request, id):
    cart = Cart.objects.get(id=id)
    cart.delete()
    return redirect('cart')

def cart_update(request,id):
    cart = Cart.objects.get(id=id)
    if request.method == "POST":
        qty = request.POST.get('qty')
        cart.qty = qty
        cart.sub_total = Decimal(qty) * cart.product.sale_price
        cart.save()
        messages.success(request, "cart updated ✅")
        return redirect('cart')
    else:
        qty = 1

def customer_orders(request):
    return render(request, 'customer/orders.html')

def create_checkout_view(request):
    carts = Cart.objects.filter(user=request.user)

    fullname = request.POST.get('fullname')
    mobile = request.POST.get('mobile')
    address = request.POST.get('address')
    city = request.POST.get('city')
    state = request.POST.get('state')

    if not all([fullname, mobile, address, city, state]):
        messages.warning(request, "All bio data is required")
        return redirect('cart')

    order = Order.objects.create(
        user=request.user,
        fullname = fullname,
        mobile = mobile,
        address = address,
        city = city,
        state = state
    )

    for each_item in carts:
        OrderItem.objects.create(
            product=each_item.product,
            order = order,
            qty = each_item.qty,
            sub_total = each_item.sub_total
        )

        order.total += each_item.sub_total
        order.save()

        
    return redirect('checkout', order.id)

def search_view(request):     
    query = request.GET.get("q")    
    
    if query:
        results = Product.objects.filter(name__icontains=query)
    else:
        return redirect('index')

    context = {
        "results": results,
        "query": query,
    }
    return render(request, "search.html", context)

def checkout_view(request, id):
    order = Order.objects.get(id=id)
    items = OrderItem.objects.filter(order=order)

    context = {
        "order": order,
        "items": items
    }
    return render(request, 'checkout.html',context)

@require_POST
def verify_payment(request):
    try:
        data = json.loads(request.body)
        reference = data.get('reference')

        if not reference:
            return JsonResponse({"status": "error", "message": "Reference missing"}, status=400)

        secret_key = settings.PAYSTACK_SECRET_KEY
        
        url = f"https://api.paystack.co/transaction/verify/{reference}"
        headers = {
            "Authorization": f"Bearer {secret_key}",
            "Content-Type": "application/json",
        }

        response = requests.get(url, headers=headers)
        res_data = response.json()
        
        print(f"Paystack Response: {res_data}")

        if res_data.get('status') is True:
            if res_data.get('data', {}).get('status') == "success":
                Cart.objects.filter(user=request.user).delete()
                return JsonResponse({"status": "success"})
            else:
                return JsonResponse({"status": "error", "message": "Transaction not successful"}, status=400)
        
        return JsonResponse({"status": "error", "message": res_data.get('message', 'Verification failed')}, status=400)

    except Exception as e:
        print(f"System Error: {str(e)}")
        return JsonResponse({"status": "error", "message": "Internal server error"}, status=500)

def payment_success(request, id):
    order = Order.objects.get(id=id)
    order.payment_status = "Paid"
    order.save()
    context = {
        "order": order,
    }
    return render(request, 'payment_success.html', context)

