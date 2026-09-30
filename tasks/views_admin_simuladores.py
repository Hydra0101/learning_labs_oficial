# Archivo: tasks/views_admin_simuladores.py
import json
import logging
import uuid
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.views.decorators.clickjacking import xframe_options_exempt

# Asegúrate de que el import de tu modelo sea correcto según tu proyecto
from .models_simuladores import SimuladorAvanzado

logger = logging.getLogger(__name__)

# =====================================================================
# 1. DASHBOARD PRINCIPAL (EL HUD DEL COMMAND CENTER)
# =====================================================================
@staff_member_required
@require_http_methods(["GET"])
def fenix_command_center(request: HttpRequest) -> HttpResponse:
    simuladores = SimuladorAvanzado.objects.all().order_by('-creado_at').defer('codigo_fuente')
    
    context = {
        'simuladores_activos': [s for s in simuladores if s.activo],
        'simuladores_cuarentena': [s for s in simuladores if not s.activo and not s.eliminado_en],
        'total_vistas': sum(s.vistas for s in simuladores)
    }
    return render(request, 'admin/simuladores/command_center.html', context)

# =====================================================================
# 2. INYECCIÓN ZERO-TRUST (API)
# =====================================================================
@staff_member_required
@require_http_methods(["POST"])
def api_inyectar_payload(request: HttpRequest) -> JsonResponse:
    try:
        data = json.loads(request.body)
        titulo = data.get('titulo', '').strip()
        codigo_html = data.get('codigo_fuente', '').strip()
        motor = data.get('motor', 'Arquitecto Elite Manual')

        if not titulo or not codigo_html:
            return JsonResponse({'error': 'Violación de protocolo: Título y Payload son obligatorios.'}, status=400)

        with transaction.atomic():
            # Generación de SLUG Criptográfico
            base_slug = titulo.lower().replace(' ', '-').replace(':', '')
            slug_final = f"{base_slug}-{uuid.uuid4().hex[:6]}"

            nuevo_simulador = SimuladorAvanzado.objects.create(
                titulo=titulo,
                slug=slug_final,
                codigo_fuente=codigo_html,
                motor_ia_generador=motor,
                activo=False, # ⚠️ NACE EN CUARENTENA OBLIGATORIA
                tasa_exito=0.0
            )

        logger.info(f"🛡️ Payload Inyectado a Cuarentena: {titulo} [{slug_final}]")
        return JsonResponse({
            'success': True,
            'slug': nuevo_simulador.slug,
            'mensaje': 'Payload aislado exitosamente en Sandbox.'
        })

    except Exception as e:
        logger.error(f"❌ Fallo crítico en inyección de payload: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

# =====================================================================
# 3. INTERRUPTOR BALÍSTICO (GO LIVE API)
# =====================================================================
@staff_member_required
@require_http_methods(["POST"])
def api_cambiar_estado(request: HttpRequest, slug: str) -> JsonResponse:
    simulador = get_object_or_404(SimuladorAvanzado, slug=slug)
    try:
        data = json.loads(request.body)
        simulador.activo = data.get('activo', False)
        simulador.save() # Llama al método save() que limpia la Memcached L4 instantáneamente
        
        estado = "EN LÍNEA" if simulador.activo else "EN CUARENTENA"
        logger.info(f"⚙️ Simulador {simulador.slug} estado cambiado a {estado}")
        
        return JsonResponse({
            'success': True, 
            'mensaje': 'El código ha sido transferido a producción global.'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# =====================================================================
# 4. SALA DE CUARENTENA (REACTOR SANDBOX)
# =====================================================================
@staff_member_required
@require_http_methods(["GET"])
def sandbox_telemetria(request: HttpRequest, slug: str) -> HttpResponse:
    simulador = get_object_or_404(SimuladorAvanzado, slug=slug)
    return render(request, 'admin/simuladores/sandbox.html', {'simulador': simulador})


# =====================================================================
# 5. RENDERIZADOR CUÁNTICO (IFRAME BYPASS)
# =====================================================================
@staff_member_required
@xframe_options_exempt
@require_http_methods(["GET"])
def render_quarantine_payload(request: HttpRequest, slug: str) -> HttpResponse:
    """
    Renderiza el código fuente en bruto.
    Ignora el filtro 'activo=True' porque es para auditoría,
    y elude el bloqueo de Clickjacking (X-Frame-Options) solo para esta vista.
    """
    simulador = get_object_or_404(SimuladorAvanzado, slug=slug)
    
    # Inyectamos el HTML directamente desde la RAM/DB al Iframe
    return HttpResponse(simulador.codigo_fuente)