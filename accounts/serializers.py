from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "role"]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
            role=validated_data.get("role", "researcher"),
        )
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Extend SimpleJWT tokens to include the user's role"""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # add custom claim
        token["role"] = getattr(user, "role", "unknown")
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # add the role into the response body as well
        data["role"] = getattr(self.user, "role", "unknown")
        return data
