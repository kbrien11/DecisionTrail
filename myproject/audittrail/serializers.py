from .models import CustomPaginator
from rest_framework import serializers


class PaginatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomPaginator
        fields = [
            "total_items",
            "total_pages",
            "current_page",
            "has_next",
            "has_previous",
        ]
