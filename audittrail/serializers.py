from .models import CustomPaginator, Decision
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


class DecisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Decision
        fields = "__all__"  # or list specific fields if needed
