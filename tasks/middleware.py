# ===================================================================
# tasks/middleware.py (COMPLETO, PROFESIONAL Y BLINDADO)
# ===================================================================
"""
Middleware personalizado para la aplicación 'tasks'.
Este módulo contiene clases de middleware que interceptan el ciclo de
petición/respuesta de Django para añadir funcionalidades transversales
a todo el sitio, como la seguridad, la gestión de sesiones y la auditoría.
"""
from django.shortcuts import redirect
from django.urls import reverse, resolve
from django.contrib import messages
# Importamos el modelo de Auditoría para registrar acciones
from .models import AuditLog

class ForcePasswordChangeMiddleware:
    """
    Middleware que obliga a los usuarios a cambiar su contraseña.
    Si un usuario autenticado tiene el atributo 'requiere_cambio_clave'
    en su perfil establecido como True, este middleware lo redirigirá
    automáticamente a la página de cambio de contraseña en cada petición.
    Se definen excepciones para rutas esenciales como la propia página de
    cambio de clave, el logout y el panel de administración de Django,
    para evitar bucles de redirección infinitos.
    """
    def __init__(self, get_response):
        """Inicializa el middleware."""
        self.get_response = get_response

    def __call__(self, request):
        """
        Este método se ejecuta en cada petición.
        Verifica el estado del usuario y redirige si es necesario.
        """
        # El middleware solo debe actuar sobre usuarios ya autenticados.
        if request.user.is_authenticated:
            
            # Rutas que siempre deben ser accesibles, incluso con el flag activo.
            # Usamos un set para una búsqueda más eficiente (O(1)).
            allowed_paths = {
                reverse('cambiar_clave'),
                reverse('signout'),
            }
            perfil = getattr(request.user, 'perfil', None)
            
            # Comprobar la condición para redirigir:
            # 1. El usuario tiene un perfil.
            # 2. El perfil requiere cambio de clave.
            # 3. La ruta solicitada NO está en las excepciones.
            # 4. La ruta solicitada NO es parte del panel de admin de Django.
            if (perfil and 
                perfil.requiere_cambio_clave and 
                request.path not in allowed_paths and
                not request.path.startswith('/admin/')):
                
                # Redirige al usuario a la vista de cambio de contraseña.
                return redirect('cambiar_clave')
        
        # Si no se cumplen las condiciones, la petición continúa su flujo normal.
        response = self.get_response(request)
        return response

# ===================================================================
# 🛡️ NUEVO MIDDLEWARE DE AUDITORÍA FORENSE (PASO 9)
# ===================================================================
class AuditMiddleware:
    """
    Middleware de Seguridad y Auditoría.
    Intercepta todas las solicitudes que modifican datos (POST, DELETE, PUT)
    y las registra en la tabla AuditLog para análisis forense.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Procesar la solicitud
        response = self.get_response(request)
        
        # Registrar la acción después de procesarla (si aplica)
        self.log_action(request)
        
        return response

    def log_action(self, request):
        """
        Registra la acción en la base de datos si cumple los criterios.
        """
        # 1. Solo registramos acciones de usuarios autenticados
        if not request.user.is_authenticated:
            return
        
        # 2. Solo registramos métodos que cambian datos (No GET, HEAD, OPTIONS)
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return
            
        # 3. Ignorar rutas irrelevantes (ej: login automático de sesión)
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return
            
        try:
            # Determinar tipo de acción para el Log
            accion_tipo = 'SENSITIVE'
            if request.method == 'POST':
                accion_tipo = 'create/update' # Simplificado, mapea a UPDATE o CREATE
            elif request.method == 'DELETE':
                accion_tipo = 'DELETE'
                
            # Obtener IP
            ip = self.get_client_ip(request)
            
            # Sanitizar datos para guardar (Ocultar passwords)
            detalles = ""
            if request.POST:
                data_copy = request.POST.copy()
                # Borrar campos sensibles
                for key in list(data_copy.keys()):
                    if 'password' in key.lower() or 'csrf' in key.lower():
                        data_copy[key] = '********'
                detalles = str(dict(data_copy))
                
            # Crear el registro en AuditLog
            # Usamos try/except para que un fallo en el log nunca detenga la app
            AuditLog.objects.create(
                usuario=request.user,
                accion=request.method, # Guardamos el método HTTP (POST, DELETE)
                modelo_afectado=request.path, # Guardamos la URL afectada como referencia
                objeto_id=None, # Opcional: Podría implementarse con signals para más precisión
                detalles=detalles[:1000], # Truncar si es muy largo
                ip_address=ip
            )
        except Exception as e:
            # En producción, usaríamos logger.error(e)
            print(f"Error en AuditMiddleware: {e}")

    def get_client_ip(self, request):
        """Obtiene la IP real del cliente."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

# ===================================================================
# 🔒 NUEVO MIDDLEWARE DE BLOQUEO PARCIAL (MODO DEGRADADO)
# ===================================================================
class BloqueoParcialMiddleware:
    """
    Guardián que intercepta todas las peticiones. Si el perfil está restringido,
    solo permite acceso a clases, simuladores, mensajes y cierre de sesión.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            perfil = getattr(request.user, 'perfil', None)
            
            if perfil and getattr(perfil, 'acceso_restringido', False):
                try:
                    ruta_actual = resolve(request.path_info).url_name
                except:
                    ruta_actual = None

                # LISTA BLANCA: URLs permitidas para usuarios bloqueados
                # Asegúrate de que estos nombres coincidan con los 'name=' de tu urls.py
                rutas_permitidas = [
                    'home', 'signout', 'logout',
                    # Mensajería
                    'buzon_mensajes', 'enviar_mensaje', 'leer_mensaje', 'marcar_leido',
                    # Clases y Motor IA
                    'lista_clases', 'ver_clase', 'class_player_view', 'ai_engine',
                    # Simuladores
                    'lista_simuladores', 'simulador_detalle',
                ]

                if ruta_actual and ruta_actual not in rutas_permitidas:
                    # Excluimos rutas estáticas y del panel de admin para evitar bloqueos visuales o del superusuario
                    if not request.path.startswith('/media/') and not request.path.startswith('/admin/') and not request.path.startswith('/static/'):
                        messages.error(request, "🛡️ ACCESO RESTRINGIDO: Por políticas de la institución, tu cuenta solo tiene habilitado el acceso a Clases, Simuladores y Mensajes.")
                        return redirect('home')

        return self.get_response(request)