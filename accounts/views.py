from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer, UserSerializer

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def whoami(request):
    user = request.user
    return Response({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
    })

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .permissions import IsAdmin

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    """
    Allows admin to list, view, and delete users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    http_method_names = ["get", "delete"]  # restricts methods to safe ones

    def get_queryset(self): #type:ignore[override]
        # Admin can see all users, researchers only themselves
        user = self.request.user
        if user.role == "admin": #type:ignore[override]
            return User.objects.all()
        return User.objects.filter(id=user.id) #type:ignore[override]
