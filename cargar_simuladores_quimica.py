import os
import sys
import time
import django

# Inicialización del entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangocrud.settings')
django.setup()

from django.db import transaction, DatabaseError
from tasks.models import Simulator

SIMULADORES_DATA = [
    {
        "title": "1. Modelos atómicos, Coulomb, Valencia y Lewis",
        "description": "Viaja al corazón cuántico de la materia. Domina los enlazamientos de Coulomb, experimenta con superposiciones de orbitales de valencia y clasifica simetrías moleculares con teoría VSEPR en fascinantes desafíos didácticos interactivos.",
        "url": "https://ai.studio/apps/0b288ecf-994a-4944-b5e0-5f078423c9c1",
        "order": 1
    },
    {
        "title": "2.2 Estructura subatómica: Protones, neutrones y electrones",
        "description": "Explora el número atómico, masa atómica y configuración de partículas fundamentales en el núcleo y la corteza electrónica.",
        "url": "https://ai.studio/apps/3e33034b-8de3-4d42-8cb0-36cc735203a9",
        "order": 2
    },
    {
        "title": "2.3 Isótopos y radioactividad básica",
        "description": "Concepto de vida media, estabilidad nuclear y aplicaciones científicas e industriales de la desintegración radiactiva.",
        "url": "https://ai.studio/apps/1a3527dd-c77b-4df5-973d-64938c03adf8",
        "order": 3
    },
    {
        "title": "2.5 La arquitectura de la Tabla Periódica",
        "description": "Grupos, periodos, metales, no metales, metaloides y tendencias periódicas visualizadas interactivamente.",
        "url": "https://ai.studio/apps/0d750f22-02f7-40c0-b5f1-f5a9d845477a",
        "order": 4
    },
    {
        "title": "3.4 Nomenclatura inorgánica (IUPAC y tradicional)",
        "description": "Aprende y pon a prueba las reglas de formulación para óxidos, ácidos, hidróxidos y sales minerales.",
        "url": "https://ai.studio/apps/a60458c2-4f41-468d-897c-daa3aad4bf46",
        "order": 5
    },
    {
        "title": "4.1 El concepto de Mol y Masa Molar",
        "description": "Comprende a fondo el Número de Avogadro, factores de conversión y masa molar estequiométrica.",
        "url": "https://ai.studio/apps/670651b2-8e83-4161-91c8-8778d6fa9072",
        "order": 6
    },
    {
        "title": "4.2 Ecuaciones químicas y tipos de reacciones",
        "description": "Interpretación visual de síntesis, descomposición, combustión y desplazamientos simples o dobles.",
        "url": "https://ai.studio/apps/1dfccc18-4eb1-4d9d-aba9-d0a7f7c39d5a?fullscreenApplet=true",
        "order": 7
    },
    {
        "title": "3.2 Enlaces intramoleculares (Iónico, covalente y metálico)",
        "description": "Analiza diferencias de electronegatividad, polaridad de enlace y propiedades de redes metálicas e iónicas.",
        "url": "https://ai.studio/apps/dcbce04e-2081-472c-be9f-ad27b85e61c3?fullscreenApplet=true",
        "order": 8
    },
    {
        "title": "Propiedades de las sustancias y enlaces químicos",
        "description": "Laboratorio analítico para contrastar puntos de fusión, conductividad y solubilidad según el tipo de enlace molecular.",
        "url": "https://ai.studio/apps/3a4a738e-4346-4725-91ef-8bbbd6ac44f7",
        "order": 9
    },
    {
        "title": "4.3 Balanceo de ecuaciones químicas (Tanteo y Redox)",
        "description": "Entrenamiento gamificado para dominar la ley de conservación de la materia por tanteo y estados de oxidación.",
        "url": "https://ai.studio/apps/e4d303e1-d19e-4148-8845-bc9d395548bb",
        "order": 10
    }
]

def ejecutar_inyeccion():
    start_time = time.time()
    print("=" * 75)
    print("⚡ [LEARNING LABS CORE ENGINE] INYECCIÓN DE CATÁLOGO CUÁNTICO DE SIMULADORES")
    print("=" * 75)
    
    insertados = 0
    actualizados = 0

    try:
        with transaction.atomic():
            for item in SIMULADORES_DATA:
                sim, created = Simulator.objects.update_or_create(
                    url=item["url"],
                    defaults={
                        "title": item["title"],
                        "subject": Simulator.SubjectChoices.QUIMICA,
                        "description": item["description"],
                        "order": item["order"],
                        "is_active": True
                    }
                )
                if created:
                    insertados += 1
                    print(f" [+] [CREATED] #{sim.order} {sim.title} (UUID: {sim.uuid})")
                else:
                    actualizados += 1
                    print(f" [~] [UPDATED] #{sim.order} {sim.title} (UUID: {sim.uuid})")

        elapsed_ms = (time.time() - start_time) * 1000
        print("-" * 75)
        print(f"✅ Transacción Completada con Éxito.")
        print(f"📊 Estadísticas: {insertados} creados | {actualizados} actualizados | {insertados + actualizados} procesados.")
        print(f"⏱️  Tiempo de Ejecución: {elapsed_ms:.2f} ms")
        print(f"🎯 Total Simuladores Activos en Sistema: {Simulator.objects.active().count()}")
        print("=" * 75)

    except DatabaseError as e:
        print(f"❌ ERROR TRANSACCIONAL EN BASE DE DATOS: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as ex:
        print(f"❌ ERROR INESPERADO: {ex}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    ejecutar_inyeccion()
