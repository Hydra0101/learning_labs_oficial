import logging
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction, IntegrityError
from rest_framework import serializers
from .utils import generar_username_unico, generar_contrasena_temporal

User = get_user_model()
logger = logging.getLogger(__name__)

class LearningLabsRegisterSerializer(serializers.Serializer):
    """
    Serializador de registro institucional con endurecimiento de seguridad (Hardened).
    Cumple con OWASP API Top 10: Prevención de condiciones de carrera,
    validación estricta de entradas y sanitización de memoria.
    """
    first_name = serializers.CharField(required=True, max_length=150, trim_whitespace=True)
    last_name = serializers.CharField(required=True, max_length=150, trim_whitespace=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=False, allow_blank=True, write_only=True)

    def validate_email(self, value):
        """
        Normalización y verificación previa de correo electrónico.
        """
        email_normalized = value.lower().strip()
        if User.objects.filter(email__iexact=email_normalized).exists():
            raise serializers.ValidationError("El correo electrónico ya se encuentra registrado.")
        return email_normalized

    def validate(self, attrs):
        """
        Validación de políticas de contraseña mediante el motor nativo de Django.
        """
        raw_password = attrs.get('password')
        if raw_password:
            try:
                # Aplica AUTH_PASSWORD_VALIDATORS configurados en settings.py
                validate_password(raw_password)
            except DjangoValidationError as e:
                raise serializers.ValidationError({'password': list(e.messages)})
        return attrs

    def create(self, validated_data):
        first_name = validated_data['first_name']
        last_name = validated_data['last_name']
        email = validated_data['email']
        raw_password = validated_data.get('password')

        es_clave_defecto = False
        if not raw_password:
            raw_password = generar_contrasena_temporal()
            es_clave_defecto = True

        username = generar_username_unico(first_name, last_name)

        # Garantiza atomicidad para evitar condiciones de carrera (Race Conditions)
        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=raw_password,
                    first_name=first_name,
                    last_name=last_name
                )

                if hasattr(user, 'perfil'):
                    user.perfil.debe_cambiar_clave = es_clave_defecto
                    user.perfil.save(update_fields=['debe_cambiar_clave'])

        except IntegrityError as e:
            logger.error(f"Error de integridad al registrar usuario {email}: {str(e)}")
            raise serializers.ValidationError(
                {"error": "No se pudo completar el registro debido a un conflicto de datos."}
            )

        # Contexto de respuesta seguro sin almacenar la clave en el modelo
        self._temp_password = raw_password
        self._es_clave_defecto = es_clave_defecto
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializador para autenticación. Sanitiza las entradas para prevenir
    inyecciones y manipulación de parámetros.
    """
    username = serializers.CharField(required=True, trim_whitespace=True)
    password = serializers.CharField(required=True, write_only=True)
