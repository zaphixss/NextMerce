from django.shortcuts import render, redirect
from .models import Category,Product, Cart, Wishlist
from userauth.models import User
from django.contrib import messages
from decimal import Decimal
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

# Create your views here.
def index(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    featured_products = Product.objects.filter(featured=True)
    best_selling = Product.objects.filter(best_selling=True)
    new_arrivals = Product.objects.filter(new_arrivals=True)

    context ={
        'categories':categories,
        'products':products,
        'featured_products':featured_products,
        'best_selling':best_selling,
        'new_arrivals':new_arrivals
    }
    return render(request, 'index.html', context)



def product_detail(request, slug):
    product = Product.objects.get(slug=slug)
    products = Product.objects.all()

    context = {
        'product': product,
        'products':products
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
    products = Product.objects.filter(best_selling=True)
    context ={
        'products':products
    }
    return render(request, 'best_selling.html', context)

def shop(request):
    products = Product.objects.filter(new_arrivals=True).order_by('id')
    categories = Category.objects.all()

    # Get the list of checked category IDs from the URL
    selected_categories = request.GET.getlist("category")

    # Filter products if categories are selected
    if selected_categories:
        products = products.filter(category_id__in=selected_categories)

   # 3. SET UP PAGINATION
    # Show 12 products per page (change 12 to whatever number you want)
    paginator = Paginator(products, 9) 
    
    # Get current page number from URL (e.g., ?page=2)
    page_number = request.GET.get('page')
    
    # Get the actual page object containing the products
    page_obj = paginator.get_page(page_number)

    context = {
        'products': page_obj,
        'categories': categories,
        'selected_categories': selected_categories, # <--- This is the variable we need in the HTML
    } 
    return render(request, 'shop.html', context)

@login_required
def user_wishlist(request):
    wishlist = Wishlist.objects.filter(user=request.user)
    context ={
        'wishlist': wishlist
    }
    return render(request, 'wishlist.html', context)

@login_required
def add_wishlist(request, id):
    product = Product.objects.get(id=id)
    
    Wishlist.objects.create(
        user = request.user,
        product = product
    )

    messages.success(request, "added to wishlist")

    return redirect(request.META.get("HTTP_REFERER", "/"))

def wishlist_delete(request, id):
    wishlist = Wishlist.objects.get(id=id)
    wishlist.delete()
    return redirect('wishlist')

@login_required
def add_to_cart(request, id):
    product = Product.objects.get(id=id)
    qauntity = int(request.POST.get("qty", 1) or 1)
    sub_total = qauntity*product.sale_price
    cart = Cart.objects.filter(user=request.user)

    context ={
        'cart':cart
    }

    if qauntity > product.qty:
        messages.warning(request, "Qty exceed")
        return redirect (request.META.get("HTTP_REFERER", "/"), context)

    item, created = Cart.objects.get_or_create(
        product = product,
        user = request.user
    )

    item.qty += qauntity
    item.sub_total = item.qty * product.sale_price
    item.save()

    
    messages.success(request, "Added to cart ✅")
    return redirect (request.META.get("HTTP_REFERER", "/"), context)

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


@login_required   
def customer_home(request):
    return render(request, 'customer/home.html')

def customer_orders(request):
    return render(request, 'customer/orders.html')