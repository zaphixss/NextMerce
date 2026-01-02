from django.shortcuts import render, redirect
from store.models import Product, Wishlist, Order, OrderItem, Reviews
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.contrib import messages

@login_required   
def customer_dashboard(request):
    orders = Order.objects.filter(user=request.user)
    wishlist = Wishlist.objects.filter(user=request.user)
    featured_products = Product.objects.filter(featured=True)
    
    items_purchased = OrderItem.objects.filter(order__in=orders, order__user=request.user)
    
    aggregation_result = Order.objects.filter(user=request.user, payment_status="Paid").aggregate(total_spent=Sum("total"))
    total_spent_value = aggregation_result['total_spent'] or 0
    
    context = {
        "orders": orders,
        "items_purchased": items_purchased,
        "total_spent": total_spent_value,
        "wishlist": wishlist,
        "featured_products": featured_products,
    }
    return render(request, 'customer/dashboard.html', context)

def order_delete(request, id):
    order =  Order.objects.get(id=id)
    order.delete()
    return redirect('customer_dashboard')

def customer_orders(request):
    orders = Order.objects.filter(user=request.user)
    context = {
        "orders": orders,
    }
    return render(request, 'customer/orders.html', context)   

def order_detail(request, id):
    order = Order.objects.get(id= id)
    items = OrderItem.objects.filter(order= order)
    context = {
        "order": order,
        "items": items,

    }
    return render(request, 'customer/order_detail.html', context)

def customer_wishlist(request):
    wishlist = Wishlist.objects.filter(user=request.user)
    context = {
        "wishlist": wishlist,

    }
    return render(request, 'customer/wishlist.html', context)

def customer_wishlist_delete(request, id):
    wishlist_item = Wishlist.objects.get(id=id)
    wishlist_item.delete()
    return redirect('customer_wishlist')

def customer_account_settings(request):
    return render(request,'customer/profile_settings.html')

def customer_profile_update(request):
    user = request.user
    if request.method == "POST":
        firstname = request.POST.get("firstname")
        lastname = request.POST.get("lastname")
        email = request.POST.get("email")
        country = request.POST.get("country")
        phone = request.POST.get("phone")
        new_image = request.FILES.get("image")
        

        user.firstname = firstname
        user.lastname = lastname
        user.email = email
        user.country = country
        user.phone = phone
        if new_image:
            user.image = new_image
        user.save()

        messages.success(request, "Profile updated successfully!")
    return redirect('customer_settings')

def customer_pending_review(request):
    pending_items = OrderItem.objects.filter(
        reviewed=False,
        order__user =request.user,
        order__payment_status= "Paid"
    ).distinct()

    context ={
        'pending_items':pending_items
    }
    return render(request, 'customer/pending_review.html', context)

def customer_review_detail(request, id):
    item = OrderItem.objects.get(id=id)
    

    if request.method == "POST":
        rating = request.POST.get("rating")
        name = request.POST.get("name")
        review = request.POST.get("review")

        if not rating:
            messages.error(request, "Please select a star rating before submitting.")
            return redirect('review_detail', id) 

        Reviews.objects.create(
            rating = rating,
            name = name,
            review = review,
            user = request.user,
            product=item.product
        )

        item.reviewed = True
        item.save()

        messages.success(request, "done!")
        return redirect('customer_reviews')


    context = {
        'item':item
    }
    return render(request, 'customer/review_detail.html', context)

