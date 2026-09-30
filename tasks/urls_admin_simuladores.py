from django.urls import path
from . import views_admin_simuladores

urlpatterns = [
    path('centro-comando/', views_admin_simuladores.fenix_command_center, name='fenix_command_center'),
    path('sandbox/<slug:slug>/', views_admin_simuladores.sandbox_telemetria, name='fenix_sandbox'),
    
    # 💥 NUEVA RUTA: El túnel de renderizado en cuarentena
    path('sandbox/render/<slug:slug>/', views_admin_simuladores.render_quarantine_payload, name='fenix_render_payload'),
    
    path('api/inyectar/', views_admin_simuladores.api_inyectar_payload, name='api_inyectar_payload'),
    path('api/toggle-estado/<slug:slug>/', views_admin_simuladores.api_cambiar_estado, name='api_cambiar_estado'),
]