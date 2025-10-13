from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "email",
            "company",
            "first_name",
            "last_name",
            "password",
            "projects",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data["username"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            email=validated_data["email"],
            company=validated_data["company"],
            password=validated_data["password"],
            projects=validated_data["projects"],
            is_active=False,
        )
        print(user)
        Token.objects.create(user=user)
        return user
