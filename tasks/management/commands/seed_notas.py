import random
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import User
from tasks.models import (
    Curso, Materia, AsignacionMateria,
    Actividad, CalificacionActividad
)

class Command(BaseCommand):
    help = "Siembra masiva de calificaciones sinteticas con distribucion estadistica real"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Iniciando Protocolo FENIX_CORE: Data Seeding..."))

        # 1. Obtener estudiantes asignados
        estudiantes = User.objects.filter(perfil__rol='ESTUDIANTE').select_related('perfil')
        if not estudiantes.exists():
            self.stdout.write(self.style.ERROR("No se encontraron estudiantes con perfil 'ESTUDIANTE'."))
            return

        # 2. Obtener asignaciones de materias activas
        asignaciones = AsignacionMateria.objects.filter(activo=True).select_related('materia', 'curso', 'docente')
        if not asignaciones.exists():
            self.stdout.write(self.style.ERROR("No hay AsignacionMateria activa. Asigna docentes a materias primero."))
            return

        self.stdout.write(f"Estudiantes detectados: {estudiantes.count()}")
        self.stdout.write(f"Asignaciones detectadas: {asignaciones.count()}")

        calificaciones_a_crear = []
        actividades_creadas = 0
        estudiantes_en_riesgo = set()

        # Marcar deliberadamente al 12% de estudiantes para activar alertas predictivas
        ids_estudiantes = list(estudiantes.values_list('id', flat=True))
        cantidad_riesgo = max(1, int(len(ids_estudiantes) * 0.12))
        riesgo_set = set(random.sample(ids_estudiantes, cantidad_riesgo))

        with transaction.atomic():
            for asignacion in asignaciones:
                # 3 actividades por materia
                for num_act in range(1, 4):
                    actividad, creada = Actividad.objects.get_or_create(
                        materia=asignacion.materia,
                        docente=asignacion.docente,
                        titulo=f"Corte {num_act}: Evaluacion Cuantitativa",
                        defaults={
                            'descripcion': f"Evaluacion acumulativa del periodo {num_act}.",
                            'porcentaje': 33,
                            'activo': True
                        }
                    )
                    if creada:
                        actividades_creadas += 1

                    # Obtener estudiantes del curso asignado
                    estudiantes_curso = estudiantes.filter(
                        inscripciones_cursos__curso=asignacion.curso,
                        inscripciones_cursos__activo=True
                    ).distinct()

                    if not estudiantes_curso.exists():
                        estudiantes_curso = estudiantes

                    for est in estudiantes_curso:
                        es_riesgo = est.id in riesgo_set

                        if es_riesgo:
                            nota = round(random.uniform(1.2, 2.9), 1)
                            estudiantes_en_riesgo.add(est.id)
                        else:
                            nota = round(random.uniform(3.3, 5.0), 1)

                        calificaciones_a_crear.append(
                            CalificacionActividad(
                                actividad=actividad,
                                estudiante=est,
                                puntaje=nota,
                                retroalimentacion="Generado sinteticamente por telemetria FENIX_CORE."
                            )
                        )

            if calificaciones_a_crear:
                CalificacionActividad.objects.bulk_create(
                    calificaciones_a_crear,
                    ignore_conflicts=True,
                    batch_size=2000
                )

        self.stdout.write(self.style.SUCCESS("INYECCION COMPLETADA CON EXITO"))
        self.stdout.write(f"Actividades estructuradas: {actividades_creadas}")
        self.stdout.write(f"Calificaciones inyectadas: {len(calificaciones_a_crear)}")
        self.stdout.write(f"Perfiles en riesgo generados: {len(estudiantes_en_riesgo)}")
        self.stdout.write(self.style.SUCCESS("Dashboards y metricas poblados correctamente."))
