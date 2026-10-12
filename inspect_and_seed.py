import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learning_labs.settings')
django.setup()

from django.apps import apps
from django.contrib.auth.models import User
import random

print("=" * 60)
print("🔍 INSPECCIÓN FORENSE DE MODELOS EN 'tasks'")
print("=" * 60)

task_models = apps.get_app_config('tasks').get_models()
model_dict = {m.__name__: m for m in task_models}

for name, model in model_dict.items():
    fields = [f.name for f in model._meta.get_fields()]
    print(f"📦 Modelo: {name}")
    print(f"   Campos: {fields}\n")

# Búsqueda heurística del modelo de notas
candidatos_nota = [m for m in model_dict.keys() if any(k in m.lower() for k in ['nota', 'calific', 'evalua', 'grade'])]
print("🎯 Posibles modelos de calificaciones detectados:", candidatos_nota)
print("=" * 60)
