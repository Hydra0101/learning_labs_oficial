#!/usr/bin/env python3
import os
import getpass
import django

# Configurar el entorno de Django para Learning Labs
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangocrud.settings')
django.setup()

from django.contrib.auth.models import User
from tasks.models import Perfil

def crear_administrador_interactivo():
    print("=" * 60)
    print("  ECOSISTEMA LEARNING LABS - REGISTRO DE ADMINISTRADOR")
    print("=" * 60)

    # 1. Solicitar datos de entrada por consola
    username = input("[+] Ingresa el nombre de usuario (username): ").strip()
    if not username:
        print("❌ Error: El nombre de usuario no puede estar vacío.")
        return

    email = input(f"[+] Ingresa el correo electrónico [{username}@learninglabs.edu.co]: ").strip()
    if not email:
        email = f"{username}@learninglabs.edu.co"

    # getpass oculta la contraseña mientras la escribes
    password = getpass.getpass("[+] Ingresa la contraseña: ").strip()
    if not password:
        print("❌ Error: La contraseña no puede estar vacía.")
        return

    confirm_password = getpass.getpass("[+] Confirma la contraseña: ").strip()
    if password != confirm_password:
        print("❌ Error: Las contraseñas no coinciden.")
        return

    # 2. Crear o actualizar el usuario en Django
    user, created = User.objects.get_or_create(
        username=username,
        defaults={'email': email}
    )

    user.set_password(password)
    user.is_staff = True
    user.is_superuser = True
    user.save()

    # 3. Crear o actualizar el Perfil con el rol de ADMINISTRADOR
    perfil, p_created = Perfil.objects.get_or_create(user=user)
    perfil.rol = 'ADMINISTRADOR'
    perfil.save()

    print("\n" + "=" * 60)
    if created:
        print(f"[✔] Superusuario/Administrador '{username}' CREADO exitosamente.")
    else:
        print(f"[✔] Usuario '{username}' ACTUALIZADO a Administrador con éxito.")
    print(f"    - ID Usuario: {user.id}")
    print(f"    - Email: {user.email}")
    print(f"    - Rol en Perfil: {perfil.rol}")
    print(f"    - Permisos: Superuser=True | Staff=True")
    print("=" * 60)

if __name__ == '__main__':
    crear_administrador_interactivo()
