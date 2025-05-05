from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response
from .models import Review, Product
from .serializers import ReviewSerializer, ProductWithReviewsSerializer
from django.shortcuts import get_object_or_404

class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        product_id = self.kwargs['product_id']
        return Review.objects.filter(product_id=product_id)
    
    def perform_create(self, serializer):
        product = get_object_or_404(Product, id=self.kwargs['product_id'])
        if Review.objects.filter(user=self.request.user, product=product).exists():
            raise serializers.ValidationError("You have already reviewed this product.")
        serializer.save(user=self.request.user, product=product)

class ProductReviewsView(generics.RetrieveAPIView):
    serializer_class = ProductWithReviewsSerializer
    queryset = Product.objects.all()
    lookup_field = 'id'