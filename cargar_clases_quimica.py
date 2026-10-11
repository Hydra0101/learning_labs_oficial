import os
import sys
import time
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangocrud.settings')
django.setup()

from django.db import transaction
from tasks.models import MasterClass

CLASES_QUIMICA_REALES = [
    {
        "order": 1,
        "title": "1.3 Propiedades de la materia",
        "description": "Físicas, químicas, intensivas y extensivas.",
        "url": "https://pub-46cdb180c9f64bb48ed13753c8e88943.r2.dev/quimica/clase%201.3%20la%20materia.mp4"
    },
    {
        "order": 2,
        "title": "1.4 El lenguaje de la medición",
        "description": "Sistema Internacional (SI), notación científica, cifras significativas y análisis dimensional.",
        "url": "https://pub-46cdb180c9f64bb48ed13753c8e88943.r2.dev/quimica/clase%201.4%20notacion%20cientifica%20parte%201.mp4"
    },
    {
        "order": 3,
        "title": "2.1 Evolución del modelo atómico",
        "description": "De Dalton al modelo mecano-cuántico y su fundamentación histórica.",
        "url": "https://pub-46cdb180c9f64bb48ed13753c8e88943.r2.dev/quimica/clase%202.1%20modelos%20atomicos%20simulador%20learning%20labs.mp4"
    },
    {
        "order": 4,
        "title": "2.2 Estructura subatómica",
        "description": "Protones, neutrones, electrones, número atómico (Z) y masa atómica (A).",
        "url": "https://pub-46cdb180c9f64bb48ed13753c8e88943.r2.dev/quimica/2.2%20Estructura%20subat%C3%B3mica%20Protones%2C%20neutrones%2C%20electrones%2C%20n%C3%BAmero%20at%C3%B3mico%20y%20masa%20at%C3%B3mica..mp4"
    },
    {
        "order": 5,
        "title": "2.3 Isótopos y radioactividad básica",
        "description": "Concepto de vida media, estabilidad nuclear y aplicaciones industriales.",
        "url": "https://pub-46cdb180c9f64bb48ed13753c8e88943.r2.dev/quimica/2.3%20Isotopos%20y%20radioactividad%20basica%20Concepto%20de%20vida%20media%20y%20aplicaciones..mp4"
    },
    {
        "order": 6,
        "title": "2.4 Configuración electrónica (Parte 1)",
        "description": "Números cuánticos, principio de Aufbau, regla de Hund y exclusión de Pauli.",
        "url": "https://pub-46cdb180c9f64bb48ed13753c8e88943.r2.dev/quimica/2.4%20Configuracion%20electronica%20Nimeros%20cuanticos%2C%20principio%20de%20Aufbau%2C%20regla%20de%20Hund%20y%20principio%20de%20exclusion%20de%20Pauli..mp4"
    },
    {
        "order": 7,
        "title": "2.4 Configuración electrónica (Parte 2)",
        "description": "Aplicación práctica avanzada: principio de Aufbau, regla de Hund y Pauli.",
        "url": "https://pub-46cdb180c9f64bb48ed13753c8e88943.r2.dev/quimica/2.4%20Configuracion%20electronica%20Nimeros%20cuanticos%2C%20principio%20de%20Aufbau%2C%20regla%20de%20Hund%20y%20principio%20de%20exclusion%20de%20Pauli.%202.mp4"
    },
    {
        "order": 8,
        "title": "2.5 Arquitectura de la Tabla Periódica",
        "description": "Grupos, periodos, metales, no metales, metaloides y tendencias periódicas.",
        "url": "https://pub-46cdb180c9f64bb48ed13753c8e88943.r2.dev/quimica/2.5%20La%20arquitectura%20de%20la%20Tabla%20Peri%C3%B3dica%20Grupos%2C%20periodos%2C%20metales%2C%20no%20metales%20y%20metaloides..mp4"
    },
    {
        "order": 9,
        "title": "3.1 Regla del octeto y estructuras de Lewis",
        "description": "Representación de electrones de valencia y enlaces moleculares.",
        "url": "https://pub-46cdb180c9f64bb48ed13753c8e88943.r2.dev/quimica/3.1%20Regla%20del%20octeto%20y%20estructuras%20de%20Lewis%20Representacin%20de%20valencia.mp4"
    },
    {
        "order": 10,
        "title": "3.2 Tipos de enlaces intramoleculares",
        "description": "Enlace iónico, covalente (polar y no polar) y metálico.",
        "url": "https://pub-46cdb180c9f64bb48ed13753c8e88943.r2.dev/quimica/3.2%20Tipos%20de%20enlaces%20intramoleculares%20I%C3%B3nico%2C%20covalente%20(polar%20y%20no%20polar)%20y%20met%C3%A1lico..mp4"
    },
    {
        "order": 11,
        "title": "3.3 Leyes de Coulomb aplicadas",
        "description": "Fuerzas electrostáticas y energía de enlace en sistemas atómicos.",
        "url": "https://pub-46cdb180c9f64bb48ed13753c8e88943.r2.dev/quimica/3.3%20leyes%20de%20coulomb%20aplicadas.mp4"
    },
    {
        "order": 12,
        "title": "3.4 Nomenclatura inorgánica: Óxidos básicos",
        "description": "Reglas de la IUPAC y sistema tradicional para la formulación de óxidos.",
        "url": "https://pub-46cdb180c9f64bb48ed13753c8e88943.r2.dev/quimica/3.4%20Nomenclatura%20inorganica%20Reglas%20de%20la%20IUPAC%20y%20sistema%20tradicional%20para%20%C3%B3xidos%20basicos.mp4"
    },
    {
        "order": 13,
        "title": "3.4 Nomenclatura inorgánica: Hidróxidos",
        "description": "Reglas de la IUPAC y sistema tradicional para hidróxidos o bases.",
        "url": "https://pub-46cdb180c9f64bb48ed13753c8e88943.r2.dev/quimica/3.4%20Nomenclatura%20inorganica%20Reglas%20de%20la%20IUPAC%20y%20sistema%20tradicional%20para%20hidroxido%203.mp4"
    },
    {
        "order": 14,
        "title": "3.4 Nomenclatura inorgánica: Ácidos",
        "description": "Reglas de la IUPAC y tradicional para hidrácidos y oxácidos.",
        "url": "https://pub-46cdb180c9f64bb48ed13753c8e88943.r2.dev/quimica/3.4%20Nomenclatura%20inorganica%20Reglas%20de%20la%20IUPAC%20y%20sistema%20tradicional%20para%20acidos%204.mp4"
    },
    {
        "order": 15,
        "title": "3.4 Nomenclatura inorgánica: Resumen general",
        "description": "Integración completa: óxidos, ácidos, hidróxidos y sales minerales.",
        "url": "https://pub-46cdb180c9f64bb48ed13753c8e88943.r2.dev/quimica/3.4%20Nomenclatura%20inorganica%20Reglas%20de%20la%20IUPAC%20y%20sistema%20tradicional%20%20resumen%20general%205.mp4"
    },
    {
        "order": 16,
        "title": "4.1 El concepto de Mol",
        "description": "Número de Avogadro, masa molar y factores de conversión estequiométricos.",
        "url": "https://pub-46cdb180c9f64bb48ed13753c8e88943.r2.dev/quimica/4.1%20El%20concepto%20de%20Mol%20N%C3%BAmero%20de%20Avogadro%20y%20masa%20molar..mp4"
    },
    {
        "order": 17,
        "title": "4.2 Ecuaciones químicas y tipos de reacciones",
        "description": "Interpretación y tipos: síntesis, descomposición, combustión y desplazamientos.",
        "url": "https://pub-46cdb180c9f64bb48ed13753c8e88943.r2.dev/quimica/4.2%20Ecuaciones%20qu%C3%ADmicas%20Interpretaci%C3%B3n%20y%20tipos%20de%20reacciones%20(s%C3%ADntesis%2C%20descomposici%C3%B3n%2C%20combusti%C3%B3n%2C%20desplazamiento%20simple%20y%20doble).mp4"
    },
    {
        "order": 18,
        "title": "4.3 Balanceo de ecuaciones: Método de tanteo",
        "description": "Método de tanteo y ley de conservación de la masa en reacciones químicas.",
        "url": "https://pub-46cdb180c9f64bb48ed13753c8e88943.r2.dev/quimica/4.3%20Balanceo%20de%20ecuaciones%20M%C3%A9todo%20de%20tanteo.mp4"
    }
]

def poblar():
    print("=" * 70)
    print("⚡ [LEARNING LABS] INYECCIÓN EXACTA DE MASTERCLASSES DE QUÍMICA")
    print("=" * 70)
    
    with transaction.atomic():
        # Limpiamos registros anteriores de química para evitar inconsistencias
        MasterClass.objects.filter(subject=MasterClass.SubjectChoices.QUIMICA).delete()
        
        insertados = 0
        for item in CLASES_QUIMICA_REALES:
            c = MasterClass.objects.create(
                order=item["order"],
                title=item["title"],
                subject=MasterClass.SubjectChoices.QUIMICA,
                description=item["description"],
                video_url=item["url"],
                duration_minutes=45,
                is_active=True
            )
            insertados += 1
            print(f" [+] [CREADA] Lección #{c.order}: {c.title}")
            
    print("-" * 70)
    print(f"✅ Inyección finalizada: {insertados} clases magistrales activas.")
    print("=" * 70)

if __name__ == '__main__':
    poblar()
