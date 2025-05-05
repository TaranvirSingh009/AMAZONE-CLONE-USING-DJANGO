from rest_framework import serializers
from .models import Review, Product

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'user', 'product', 'rating', 'comment', 'created_at']
        read_only_fields = ['user', 'created_at']
        extra_kwargs = {
            'product': {'required': True}
        }

class ProductWithReviewsSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'image_url', 'stock', 
                 'category', 'reviews', 'average_rating']
    
    def get_average_rating(self, obj):
        return obj.average_rating()