from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Category, Product, CartItem, Order, OrderItem

# Custom User Admin to display all fields
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_admin', 'is_staff')
    list_filter = ('is_admin', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Permissions', {'fields': ('is_admin', 'is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_admin', 'is_staff'),
        }),
    )
    search_fields = ('email', 'username')
    ordering = ('email',)

# Category Admin with improved display
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
   

# Product Admin with filters and search
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock')
    list_filter = ('category',)
    search_fields = ('name', 'description')
    raw_id_fields = ('category',)  # Better for large category lists
    list_editable = ('price', 'stock')  # Allows inline editing

# Order Item inline for Order admin
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ('product',)
    extra = 0  # Don't show empty extra fields

# Order Admin with detailed view
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'user__email')
    inlines = (OrderItemInline,)
    date_hierarchy = 'created_at'

# Cart Item Admin
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity')
    list_filter = ('user',)
    raw_id_fields = ('user', 'product')

# Register all models
admin.site.register(User, CustomUserAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)