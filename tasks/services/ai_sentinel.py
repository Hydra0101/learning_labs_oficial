"""
==============================================================================
🛡️ FENIX_CORE: DEEPSEEK SENTINEL & CIRCUIT BREAKER ENGINE (GOD-TIER V3)
==============================================================================
Arquitectura defensiva Zero-Trust de grado militar.
- Resiliencia híbrida: Redis Cluster / LocMemCache / In-Process Fallback.
- Supresión atómica de bucles y prevención de token exhaustion leaks.
- Telemetría en microsegundos y persistencia forense en AIUsageLog.
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
# ⚙️ PARÁMETROS DE GOBERNANZA TÁCTICA (HARD LIMITS INMUTABLES)
# ==============================================================================
MAX_INPUT_CHARS: int = 2500           # Límite estricto de entrada por mensaje
MAX_OUTPUT_TOKENS: int = 400          # Techo duro de facturación por completion
SLIDING_WINDOW_SECONDS: int = 60      # Ventana de auditoría temporal (1 minuto)
MAX_REQUESTS_PER_WINDOW: int = 8      # Límite estándar por usuario / minuto
CIRCUIT_BREAKER_LIMIT: int = 18       # Umbral crítico de corte por bucle anómalo
CIRCUIT_BREAKER_COOLDOWN: int = 900   # Cuarentena estricta (15 minutos = 900 seg)

# Fallback en RAM de proceso si Django Cache / Redis colapsa
_IN_MEMORY_CIRCUIT_FALLBACK: Dict[str, Dict[str, Any]] = {}


class TokenCircuitBreakerException(Exception):
    """Excepción táctica disparada al interceptar bucles o tráfico anómalo."""
    pass


class AISentinelService:
    def __init__(self):
        self.api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
        self.client = OpenAI(
            api_key=self.api_key or "mock-key-preventiva",
            base_url="https://api.deepseek.com",
            timeout=12.0,   # Falla rápido: Protege workers de Gunicorn / Daphne
            max_retries=0   # CERO RETRIES: Regla de oro contra avalanchas de facturación
        )

    @staticmethod
    def _hash_id(raw_id: str) -> str:
        """Genera un hash criptográfico SHA-256 (truncado) para aislamiento en caché."""
        return hashlib.sha256(str(raw_id).encode("utf-8")).hexdigest()[:16]

    def _evaluar_circuito(self, user_id: str) -> None:
        """
        Evalúa el estado del circuito con tolerancia a fallos absolutos.
        """
        safe_id = self._hash_id(user_id)
        trip_key = f"fenix:circuit_trip:{safe_id}"
        window_id = int(time.time() // SLIDING_WINDOW_SECONDS)
        counter_key = f"fenix:rate_limit:{safe_id}:{window_id}"
        
        # 1. Verificación de cuarentena previa (Circuit Breaker Tripped)
        is_tripped = False
        try:
            is_tripped = bool(cache.get(trip_key))
        except Exception:
            proc_trip = _IN_MEMORY_CIRCUIT_FALLBACK.get(trip_key)
            if proc_trip and proc_trip.get("expire", 0) > time.time():
                is_tripped = True

        if is_tripped:
            logger.warning(f"[SENTINEL] Rechazo silencioso. Tráfico bloqueado para ID Hash: {safe_id}")
            raise TokenCircuitBreakerException(
                "🚨 Modo cuarentena activo: Tráfico bloqueado temporalmente por prevención de bucles."
            )

        # 2. Conteo atómico en ventana deslizante (Blindaje Anti-TypeError)
        current_hits: Optional[int] = None
        try:
            current_hits = cache.incr(counter_key)
        except (ValueError, Exception):
            current_hits = None

        if current_hits is None:
            try:
                # Fallback para LocMemCache o cachés que no soportan incr()
                val = cache.get(counter_key)
                if val is None or not isinstance(val, int):
                    cache.set(counter_key, 1, timeout=SLIDING_WINDOW_SECONDS * 2)
                    current_hits = 1
                else:
                    current_hits = val + 1
                    cache.set(counter_key, current_hits, timeout=SLIDING_WINDOW_SECONDS * 2)
            except Exception:
                # Supervivencia nivel núcleo: Fallback a variable en memoria de proceso
                mem_data = _IN_MEMORY_CIRCUIT_FALLBACK.setdefault(counter_key, {"hits": 0, "expire": time.time() + SLIDING_WINDOW_SECONDS})
                mem_data["hits"] += 1
                current_hits = mem_data["hits"]

        # 3. Disparo del Disyuntor (Detección de Bucle Anómalo)
        if current_hits > CIRCUIT_BREAKER_LIMIT:
            try:
                cache.set(trip_key, True, timeout=CIRCUIT_BREAKER_COOLDOWN)
            except Exception:
                pass
            _IN_MEMORY_CIRCUIT_FALLBACK[trip_key] = {"expire": time.time() + CIRCUIT_BREAKER_COOLDOWN}
            
            logger.critical(
                f"[DEFENSA ACTIVA] 🛑 CIRCUITO DISPARADO: {current_hits} reqs/min. Bloqueando hash {safe_id} por 15m."
            )
            raise TokenCircuitBreakerException("🚨 Modo cuarentena: Avalancha de peticiones interceptada por el núcleo.")

        # 4. Limitador de Tasa Normal por Ventana
        if current_hits > MAX_REQUESTS_PER_WINDOW:
            raise TokenCircuitBreakerException("⏳ Capacidad de transmisión alcanzada. Aguarda unos segundos.")

    def _sanear_historial(self, historial: Optional[List[Dict[str, str]]], query_actual: str) -> List[Dict[str, str]]:
        """
        Compresión destructiva de contexto:
        Poda payloads masivos y restringe el contexto a las últimas rondas de conversación.
        """
        query_sanitizada = str(query_actual)[:MAX_INPUT_CHARS].strip()
        historial_seguro = historial if isinstance(historial, list) else []

        # Poda agresiva: máximo 4 mensajes previos (2 turnos)
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
            if isinstance(msg, dict) and msg.get("role") in ("user", "assistant"):
                contenido = str(msg.get("content", ""))[:600].strip()
                if contenido:
                    mensajes_finales.append({"role": msg["role"], "content": contenido})

        mensajes_finales.append({"role": "user", "content": query_sanitizada})
        return mensajes_finales

    def _registrar_telemetria_db(self, user_id: str, prompt_t: int, comp_t: int, duracion: float, exito: bool, err: str = "") -> None:
        """Guarda el log de auditoría forense en BD de forma silenciosa y no bloqueante."""
        try:
            from tasks.models import AIUsageLog
            AIUsageLog.objects.create(
                usuario_id=user_id if str(user_id).isdigit() else None,
                rol_usado="STRATOS_SOCRATICO",
                accion="CHAT_QUERY",
                modelo_utilizado="deepseek-chat",
                tokens_entrada=prompt_t,
                tokens_salida=comp_t,
                tiempo_ejecucion=duracion,
                exitoso=exito,
                error_mensaje=err[:250] if err else "",
                metadata_tecnica={"hash": self._hash_id(user_id)}
            )
        except Exception:
            pass

    def ejecutar_chat(self, user_id: str, query: str, historial: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """Punto de entrada unificado y transaccional para la invocación a la IA."""
        
        # 1. Modo Sandbox de costo $0 si no hay llave real configurada
        if not self.api_key or self.api_key.startswith("mock"):
            logger.info("🟢 [SIMULACIÓN LOCAL] Query auditada con éxito. Consumo $0.")
            return {
                "success": True,
                "content": f"[Modo Sandbox]: Conexión simulada con éxito. Mensaje recibido: '{query[:40]}...'"
            }

        # 2. Evaluación del Cortafuegos (Circuit Breaker)
        try:
            self._evaluar_circuito(user_id)
        except TokenCircuitBreakerException as err:
            return {"success": False, "content": str(err), "circuit_tripped": True}

        # 3. Poda y estructuración del payload
        payload = self._sanear_historial(historial, query)

        # 4. Invocación segura y telemetría de microsegundos
        inicio = time.perf_counter()
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=payload,
                max_tokens=MAX_OUTPUT_TOKENS,
                temperature=0.3,
                stream=False
            )
            latencia = round(time.perf_counter() - inicio, 3)
            uso = response.usage

            # Telemetría de consola en tiempo real
            print(
                f"📊 [TELEMETRÍA] ID: {self._hash_id(user_id)} | In: {uso.prompt_tokens}t | "
                f"Out: {uso.completion_tokens}t | Tot: {uso.total_tokens}t | Lat: {latencia}s"
            )

            # Persistencia forense en base de datos
            self._registrar_telemetria_db(
                user_id=user_id,
                prompt_t=uso.prompt_tokens,
                comp_t=uso.completion_tokens,
                duracion=latencia,
                exito=True
            )

            return {
                "success": True,
                "content": response.choices[0].message.content.strip()
            }

        except AuthenticationError:
            latencia = round(time.perf_counter() - inicio, 3)
            self._registrar_telemetria_db(user_id, 0, 0, latencia, False, "AuthenticationError")
            logger.critical("[CORTAFUEGOS] API Key rechazada por DeepSeek.")
            return {"success": False, "content": "Falla de autenticación en las credenciales de IA."}

        except RateLimitError:
            latencia = round(time.perf_counter() - inicio, 3)
            self._registrar_telemetria_db(user_id, 0, 0, latencia, False, "RateLimitError")
            logger.warning("[CUELLO DE BOTELLA] Límite alcanzado en el proveedor DeepSeek.")
            return {"success": False, "content": "Saturación detectada en el servicio externo."}

        except APIConnectionError:
            latencia = round(time.perf_counter() - inicio, 3)
            self._registrar_telemetria_db(user_id, 0, 0, latencia, False, "APIConnectionError")
            logger.error("[ENLACE ROTO] Conexión caída con el endpoint de DeepSeek.")
            return {"success": False, "content": "Error de enlace con el servidor de IA."}

        except Exception as e:
            latencia = round(time.perf_counter() - inicio, 3)
            self._registrar_telemetria_db(user_id, 0, 0, latencia, False, str(e))
            logger.error(f"[EXCEPCIÓN CRÍTICA] {str(e)}", exc_info=True)
            return {"success": False, "content": "Ruptura temporal en la capa de procesamiento."}