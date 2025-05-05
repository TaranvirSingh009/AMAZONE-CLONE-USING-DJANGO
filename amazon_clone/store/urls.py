from django.urls import path
from . import views
from .views_api import ReviewListCreateView, ProductReviewsView
from django.urls import include, path
from rest_framework.routers import DefaultRouter

app_name = 'store'

urlpatterns = [
    path('', views.home, name='home'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/register/', views.register, name='register'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('products/', views.catalog, name='catalog'),
    path('products/<int:id>/', views.product_detail, name='product_detail'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('checkout/', views.checkout_process, name='checkout_process'),
    path('api/products/<int:product_id>/reviews/', ReviewListCreateView.as_view(), name='product-reviews'),
    path('api/products/<int:id>/with-reviews/', ProductReviewsView.as_view(), name='product-with-reviews'),
    path('feedback/<int:order_id>/', views.feedback_view, name='feedback'),
]