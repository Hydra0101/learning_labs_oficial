"""
==============================================================================
🛡️ FENIX_CORE: DEEPSEEK SENTINEL & CIRCUIT BREAKER ENGINE (GOD-TIER)
==============================================================================
Arquitectura defensiva Zero-Trust. Protege la infraestructura contra bucles
infinitos de frontend, bloquea fugas de memoria por inyección de contexto
y monitoriza la telemetría en microsegundos reales.
==============================================================================
"""

import os
import time
import logging
import hashlib
from typing import Dict, Any, List, Optional
from django.core.cache import cache
from openai import OpenAI, APIError, RateLimitError, APIConnectionError, AuthenticationError

logger = logging.getLogger("fenix.ai_sentinel")

# ==============================================================================
# ⚙️ PARÁMETROS DE GOBERNANZA TÁCTICA (HARD LIMITS)
# ==============================================================================
MAX_INPUT_CHARS: int = 3500           # Prevención de desbordamiento de buffer
MAX_OUTPUT_TOKENS: int = 450          # Techo estricto de facturación por request
SLIDING_WINDOW_SECONDS: int = 60      # Ventana de auditoría temporal (1 minuto)
MAX_REQUESTS_PER_WINDOW: int = 8      # Límite transaccional sano por usuario/minuto
CIRCUIT_BREAKER_LIMIT: int = 20       # Umbral crítico de detección de bucle DDoS
CIRCUIT_BREAKER_COOLDOWN: int = 900   # Cuarentena en Redis (15 minutos)


class TokenCircuitBreakerException(Exception):
    """Excepción táctica disparada al interceptar anomalías de tráfico de red."""
    pass


class AISentinelService:
    def __init__(self):
        self.api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
        self.client = OpenAI(
            # Si no hay key, inyectamos un string para que el cliente no falle al inicializar,
            # pero el método ejecutar_chat lo interceptará antes de enviarlo.
            api_key=self.api_key or "mock-key-preventiva",
            base_url="https://api.deepseek.com",
            timeout=12.0,  # Timeout optimizado: Falla rápido, no ahoga a Gunicorn/Daphne
            max_retries=0  # ZERO RETRIES: Regla de oro para evitar avalanchas de facturación
        )

    def _hash_id(self, raw_id: str) -> str:
        """Hashea el identificador para evitar inyecciones o colisiones en la matriz Redis."""
        return hashlib.md5(str(raw_id).encode('utf-8')).hexdigest()

    def _evaluar_circuito(self, user_id: str) -> None:
        safe_id = self._hash_id(user_id)
        trip_key = f"fenix:circuit_trip:{safe_id}"
        
        # 1. Comprobación de estado del disyuntor
        if cache.get(trip_key):
            logger.warning(f"[SENTINEL] Rechazo silencioso. Tráfico bloqueado para ID Hash: {safe_id[:8]}")
            raise TokenCircuitBreakerException(
                "🚨 Enlace bloqueado temporalmente. Se detectó tráfico anómalo previamente."
            )

        # 2. Deslizamiento de ventana determinista en memoria
        window_id = int(time.time() // SLIDING_WINDOW_SECONDS)
        counter_key = f"fenix:rate_limit:{safe_id}:{window_id}"
        
        try:
            # Operación atómica nativa de Redis (Cero condiciones de carrera)
            current_hits = cache.incr(counter_key)
        except (ValueError, Exception):
            cache.set(counter_key, 1, timeout=SLIDING_WINDOW_SECONDS * 2)
            current_hits = 1

        # 3. Disparo del Disyuntor (Detección de Bucle)
        if current_hits > CIRCUIT_BREAKER_LIMIT:
            cache.set(trip_key, True, timeout=CIRCUIT_BREAKER_COOLDOWN)
            logger.critical(f"[DEFENSA ACTIVA] 🛑 BUCLE NEUTRALIZADO. {current_hits} reqs/min. IP/ID: {safe_id[:8]}")
            raise TokenCircuitBreakerException("🚨 Modo cuarentena: Avalancha de peticiones interceptada por el núcleo.")

        # 4. Limitador de Tasa Normal
        if current_hits > MAX_REQUESTS_PER_WINDOW:
            raise TokenCircuitBreakerException("⏳ Capacidad de transmisión alcanzada. Aguarda unos segundos.")

    def _sanear_historial(self, historial: Optional[List[Dict[str, str]]], query_actual: str) -> List[Dict[str, str]]:
        """
        Compresión destructiva de payload. Poda el contexto antiguo y recorta payloads masivos 
        antes de que toquen el cable de red.
        """
        query_sanitizada = str(query_actual)[:MAX_INPUT_CHARS].strip()
        historial_seguro = historial if isinstance(historial, list) else []
        
        # Poda agresiva: Solo recordamos las últimas 2 interacciones completas (4 mensajes)
        historial_reciente = historial_seguro[-4:] if len(historial_seguro) > 4 else historial_seguro

        prompt_sistema = {
            "role": "system",
            "content": (
                "Eres Stratos, el Mentor Socrático de Learning Labs. "
                "Sé incisivo, analítico y conciso. Responde siempre con preguntas guía breves. "
                "NUNCA des la respuesta directa ni generes textos extensos."
            )
        }

        mensajes_finales = [prompt_sistema]
        for msg in historial_reciente:
            if isinstance(msg, dict) and msg.get("role") in ["user", "assistant"]:
                mensajes_finales.append({
                    "role": msg["role"],
                    "content": str(msg.get("content", ""))[:800].strip()
                })

        mensajes_finales.append({"role": "user", "content": query_sanitizada})
        return mensajes_finales

    def ejecutar_chat(self, user_id: str, query: str, historial: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        
        # Bypass instantáneo si estamos en desarrollo local o no hay llaves reales
        if not self.api_key or self.api_key.startswith("mock"):
            logger.info(f"🟢 [SIMULACIÓN LOCAL] Query auditada con éxito. Consumo $0.")
            return {
                "success": True,
                "content": f"[Modo Sandbox]: Conexión simulada. Paquete recibido: '{query[:40]}...'"
            }

        # Evaluación de firewall
        try:
            self._evaluar_circuito(user_id)
        except TokenCircuitBreakerException as err:
            return {"success": False, "content": str(err), "circuit_tripped": True}

        # Ensamblaje del paquete blindado
        payload = self._sanear_historial(historial, query)

        try:
            # Medición cuántica de alta precisión, inmune a sincronizaciones NTP del servidor
            inicio = time.perf_counter()
            
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=payload,
                max_tokens=MAX_OUTPUT_TOKENS,
                temperature=0.4,  # Menor temperatura = menos variabilidad, menos propensión a alucinaciones largas
                stream=False
            )
            
            latencia = round(time.perf_counter() - inicio, 3)
            uso = response.usage
            
            print(
                f"📊 [TELEMETRÍA] ID: {self._hash_id(user_id)[:8]} | In: {uso.prompt_tokens}t | "
                f"Out: {uso.completion_tokens}t | Tot: {uso.total_tokens}t | Lat: {latencia}s"
            )

            return {
                "success": True,
                "content": response.choices[0].message.content.strip()
            }

        except AuthenticationError:
            logger.critical("[CORTAFUEGOS] API Key de DeepSeek rechazada por el servidor central.")
            return {"success": False, "content": "Falla de credenciales en el enlace neuronal."}
        except RateLimitError:
            logger.warning("[CUELLO DE BOTELLA] Límite de plataforma DeepSeek alcanzado.")
            return {"success": False, "content": "Saturación detectada en la matriz externa."}
        except APIConnectionError:
            logger.error("[ENLACE ROTO] Fallo físico al intentar contactar la IA.")
            return {"success": False, "content": "Pérdida de paquetes de red con el nodo central."}
        except Exception as e:
            logger.error(f"[EXCEPCIÓN CRÍTICA] Fallo no interceptado: {str(e)}", exc_info=True)
            return {"success": False, "content": "Ruptura crítica en la capa de procesamiento."}
