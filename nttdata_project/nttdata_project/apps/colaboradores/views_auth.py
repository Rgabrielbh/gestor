from django.utils.translation import gettext_lazy as _
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .models import Colaborador
from .serializers import LoginSerializer, RegisterSerializer, MeSerializer, ChangePasswordSerializer, ColaboradorDetailSerializer


class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {"id": user.id, "username": user.username, "nome": user.nome_display,
                     "email": user.email, "role": user.role, "role_display": user.get_role_display(),
                     "avatar": user.avatar.url if user.avatar else None},
        })


class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail": _("Campo 'refresh' obrigatório.")}, status=400)
        try:
            RefreshToken(refresh_token).blacklist()
        except TokenError as e:
            return Response({"detail": str(e)}, status=400)
        return Response({"detail": _("Logout realizado.")}, status=status.HTTP_205_RESET_CONTENT)


class RegisterAPIView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        if not request.user.role in ("diretor", "gestor"):
            return Response({"detail": _("Apenas Gestores ou Diretores podem criar colaboradores.")}, status=403)
        return super().post(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        colaborador = serializer.save()
        refresh = RefreshToken.for_user(colaborador)
        return Response({
            "detail": _("Colaborador criado."),
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "colaborador": ColaboradorDetailSerializer(colaborador).data,
        }, status=status.HTTP_201_CREATED)


class MeAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MeSerializer

    def get_object(self):
        return self.request.user


class ChangePasswordAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": _("Senha alterada.")})
