from .models import Cart, Wishlist, Category 

def cart_wishlist_counts(request):
    cart_count = 0
    wishlist_count = 0
    
    if request.user.is_authenticated:
        cart_count = Cart.objects.filter(user=request.user).count()
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
    
    return {
        'CART_ITEM_COUNT': cart_count,
        'WISHLIST_ITEM_COUNT': wishlist_count,
    }

def default(request):
    categories = Category.objects.all()

    return {
        'categories': categories,
    }

