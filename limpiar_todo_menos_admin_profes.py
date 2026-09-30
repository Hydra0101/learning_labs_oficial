#!/usr/bin/env python3
import os
import django

# Configurar el módulo de settings oficial de Learning Labs (djangocrud)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangocrud.settings')
django.setup()

from django.contrib.auth.models import User
from django.apps import apps

def ejecutar_limpieza():
    print("=" * 65)
    print("  ECOSISTEMA LEARNING LABS - PURGA DE BASE DE DATOS")
    print("=" * 65)
    print("[i] Objetivo: Conservar Administradores y Profesores.")
    print("[i] Eliminando: Estudiantes, Acudientes, Cursos, Notas y Boletines.\n")

    # 1. Identificar Administradores y Profesores
    # Se filtran superusuarios, personal de staff y cuentas asociadas a roles de docente
    query_admins = User.objects.filter(is_superuser=True) | User.objects.filter(is_staff=True)
    query_profes = User.objects.filter(groups__name__icontains='profesor') | User.objects.filter(username__icontains='profe')
    
    usuarios_conservar = (query_admins | query_profes).distinct()
    ids_conservar = set(usuarios_conservar.values_list('id', flat=True))

    print(f"[*] Usuarios detectados a CONSERVAR ({len(ids_conservar)} en total):")
    for usr in usuarios_conservar:
        rol = "ADMIN / SUPERUSER" if usr.is_superuser else ("STAFF" if usr.is_staff else "PROFESOR")
        print(f"    - ID: {usr.id:<3} | Username: {usr.username:<20} | Rol: {rol}")

    # 2. Confirmación de seguridad
    print("\n" + "!" * 65)
    confirmacion = input("¿Confirmas la eliminación masiva de los demás registros? (s/N): ")
    if confirmacion.lower() != 's':
        print("[!] Operación cancelada. No se realizaron cambios.")
        return

    # 3. Eliminar usuarios (Estudiantes y Acudientes)
    usuarios_eliminar = User.objects.exclude(id__in=ids_conservar)
    total_usuarios = usuarios_eliminar.count()
    
    # La eliminación en cascada de Django borrará perfiles y relaciones dependientes
    usuarios_eliminar.delete()
    print(f"\n[✔] Eliminados {total_usuarios} usuarios (Estudiantes/Acudientes).")

    # 4. Limpieza de modelos académicos (Cursos, Materias, Boletines, Registros)
    for model in apps.get_models():
        model_name = model.__name__.lower()
        # Se omiten las tablas del sistema de autenticación de Django
        if model._meta.app_label in ['auth', 'sessions', 'contenttypes', 'admin']:
            continue
            
        # Si el modelo no es User, se purgan sus registros académicos
        if model_name not in ['user', 'group', 'permission']:
            try:
                registros_eliminados, _ = model.objects.all().delete()
                if registros_eliminados > 0:
                    print(f"[✔] Purgado modelo '{model.__name__}': {registros_eliminados} registros borrados.")
            except Exception as e:
                print(f"[!] Aviso al limpiar {model.__name__}: {e}")

    print("\n" + "=" * 65)
    print("  ¡BASE DE DATOS LIMPIA Y LISTA PARA PRUEBAS EN LEARNING LABS!")
    print("=" * 65)

if __name__ == '__main__':
    ejecutar_limpieza()
