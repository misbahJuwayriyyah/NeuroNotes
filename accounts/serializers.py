from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "password", "role"]

    def create(self, validated_data):
        user = User.objects.create_user( #type: ignore
            email=validated_data["email"],
            password=validated_data["password"],
            role=validated_data.get("role", "researcher"),
        )
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Extend SimpleJWT tokens to include the user's role."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = getattr(user, "role", "unknown")
        return token

    def validate(self, attrs):
        # JWT login now expects 'email' instead of 'username'
        username_field = User.EMAIL_FIELD
        attrs[username_field] = attrs.get("email", None)
        data = super().validate(attrs)
        data["role"] = getattr(self.user, "role", "unknown")
        return data
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "username", "role"]

