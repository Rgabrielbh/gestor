from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from .models import Colaborador, RoleChoices


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(label=_("Usuário ou e-mail"))
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate(self, attrs):
        username = attrs.get("username", "").strip()
        password = attrs.get("password", "")
        if "@" in username:
            try:
                user = Colaborador.objects.get(email__iexact=username)
                username = user.username
            except Colaborador.DoesNotExist:
                pass
        user = authenticate(request=self.context.get("request"), username=username, password=password)
        if not user:
            raise serializers.ValidationError(_("Credenciais inválidas."), code="authorization")
        if not user.is_active:
            raise serializers.ValidationError(_("Conta desativada."), code="inactive")
        attrs["user"] = user
        return attrs


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password], style={"input_type": "password"})
    password_confirm = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        model = Colaborador
        fields = ["username","email","nome","password","password_confirm","role","matricula",
                  "cargo","funcao","telefone","cidade","estado","local_escritorio","dt_admissao"]
        extra_kwargs = {"email": {"required": True}, "nome": {"required": True}}

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password_confirm"):
            raise serializers.ValidationError({"password_confirm": _("Senhas não coincidem.")})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = Colaborador(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        if not self.context["request"].user.check_password(value):
            raise serializers.ValidationError(_("Senha atual incorreta."))
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError({"new_password_confirm": _("Senhas não coincidem.")})
        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


class ColaboradorListSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source="get_role_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    gestor_nome = serializers.CharField(source="gestor_direto.nome", read_only=True)

    class Meta:
        model = Colaborador
        fields = ["id","username","nome","email","matricula","cargo","funcao","cidade",
                  "estado","local_escritorio","role","role_display","status","status_display",
                  "dt_admissao","dt_demissao","telefone","gestor_direto","gestor_nome","avatar"]


class ColaboradorDetailSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source="get_role_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    gestor_nome = serializers.CharField(source="gestor_direto.nome", read_only=True)

    class Meta:
        model = Colaborador
        fields = ["id","username","nome","email","matricula","pos","req","cargo","funcao",
                  "telefone","cidade","estado","local_escritorio","dt_admissao","dt_demissao",
                  "salario","cod_gestor_sup","cod_gestor","nome_gestor","gestor_direto","gestor_nome",
                  "status","status_display","role","role_display","avatar","date_joined","last_login"]
        read_only_fields = ["date_joined","last_login"]


class MeSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source="get_role_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Colaborador
        fields = ["id","username","nome","email","matricula","cargo","funcao","telefone",
                  "cidade","estado","local_escritorio","dt_admissao","role","role_display",
                  "status","status_display","avatar","date_joined","last_login"]
        read_only_fields = ["date_joined","last_login","role"]
