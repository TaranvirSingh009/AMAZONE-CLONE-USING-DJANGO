from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import User, Product, Category, CartItem, Order, OrderItem
from .forms import RegistrationForm, LoginForm
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def home(request):
    categories = Category.objects.all()
    featured_products = Product.objects.all()[:4]
    return render(request, 'home.html', {
        'categories': categories,
        'featured_products': featured_products
    })

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('store:home')
            else:
                messages.error(request, 'Invalid email or password')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LoginForm()
    return render(request, 'auth/login.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.username = form.cleaned_data['username']
            user.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('store:home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = RegistrationForm()
    return render(request, 'auth/register.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('store:home')

def catalog(request):
    # Only initialize sample data if no products exist and we're not in a migration
    if not Product.objects.exists() and not getattr(settings, 'MIGRATION_MODULES', None):
        try:
            initialize_sample_data()
        except Exception as e:
            # Log the error but don't crash the view
            print(f"Error initializing sample data: {e}")
    
    category_id = request.GET.get('category')
    search = request.GET.get('search', '')
    sort = request.GET.get('sort', 'name')
    
    products = Product.objects.all()
    
    if category_id:
        products = products.filter(category_id=category_id)
    if search:
        products = products.filter(Q(name__icontains=search))
    
    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    else:
        products = products.order_by('name')
    
    categories = Category.objects.all()
    return render(request, 'products/catalog.html', {
        'products': products,
        'categories': categories
    })

def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'products/product_details.html', {'product': product})

@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'cart/cart.html', {
        'cart_items': cart_items,
        'total': total
    })

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    
    return redirect('store:view_cart')

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    return redirect('store:view_cart')

@login_required
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > 0 and quantity <= cart_item.product.stock:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, 'Cart updated successfully')
    else:
        messages.error(request, 'Invalid quantity')
    
    return redirect('store:view_cart')

@login_required
def checkout_process(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.product.price * item.quantity for item in cart_items)
    
    if request.method == 'POST':
        if not cart_items.exists():
            messages.error(request, 'Your cart is empty')
            return redirect('store:view_cart')
        
        order = Order.objects.create(
            user=request.user,
            total_amount=total
        )
        
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
        
        cart_items.delete()
        messages.success(request, 'Order placed successfully!')
        return redirect('store:home')
    
    return render(request, 'checkout/checkout.html', {
        'cart_items': cart_items,
        'total': total
    })

def initialize_sample_data():
    # Create categories first
    electronics = Category.objects.create(
        name='Electronics',
        description='Latest gadgets and electronics',
        banner_url='https://images.unsplash.com/photo-1498049794561-7780e7231661?w=500'
    )
    
    books = Category.objects.create(
        name='Books',
        description='Books across all genres',
        banner_url='https://images.unsplash.com/photo-1495446815901-a7297e633e8d?w=500'
    )
    
    fashion = Category.objects.create(
        name='Fashion',
        description='Trendy clothing and accessories',
        banner_url='https://images.unsplash.com/photo-1445205170230-053b83016050?w=500'
    )
    
    # Create products with proper category references
    products = [
        {'name': 'Wireless Headphones', 'price': 99.99, 'category': electronics,
         'image_url': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500',
         'description': 'High-quality wireless headphones with noise cancellation', 'stock': 100},

        {'name': 'Smart Watch', 'price': 199.99, 'category': electronics,
         'image_url': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500',
         'description': 'Feature-rich smartwatch with fitness tracking', 'stock': 100},

        {'name': 'Best Seller Book', 'price': 19.99, 'category': books,
         'image_url': 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=500',
         'description': 'International bestseller, must read', 'stock': 100},

        {'name': 'Designer T-Shirt', 'price': 29.99, 'category': fashion,
         'image_url': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=500',
         'description': 'Comfortable cotton t-shirt with modern design', 'stock': 100},

        {'name': 'Laptop Pro', 'price': 1299.99, 'category': electronics,
         'image_url': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500',
         'description': 'Powerful laptop for professionals', 'stock': 100},

        {'name': 'Classic Novel', 'price': 15.99, 'category': books,
         'image_url': 'https://images.unsplash.com/photo-1543002588-bfa74002ed7e?w=500',
         'description': 'Timeless classic literature', 'stock': 100}
    ]
    
    for product_data in products:
        Product.objects.create(**product_data)