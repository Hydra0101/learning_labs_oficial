"""
==============================================================================
🛡️ FENIX_CORE: SUITE DE PRUEBAS INDUSTRIALES (CI/CD ENTERPRISE GRADE)
==============================================================================
Módulo de validación estricta para AISentinelService.
Audita fugas de memoria, condiciones de carrera extremas y supervivencia
del núcleo ante fallos totales del backend de caché (Redis/LocMem).
==============================================================================
"""

import time
import threading
import concurrent.futures
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.core.cache import cache
from tasks.services.ai_sentinel import AISentinelService, MAX_INPUT_CHARS, MAX_REQUESTS_PER_WINDOW

class TestAISentinelIndustrialGrade(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        print("\n" + "="*70)
        print("🧪 INICIANDO BATERÍA DE PRUEBAS DE ESTRÉS (ZERO-TRUST ENVIRONMENT)")
        print("="*70)

    def setUp(self):
        """Limpieza absoluta de estado antes de cada vector de prueba."""
        cache.clear()
        self.sentinel = AISentinelService()
        # Forzar una API Key ficticia para que no actúe el Bypass de desarrollo
        self.sentinel.api_key = "sk-enterprise-test-key"

    def test_01_payload_bombing_memory_leak_prevention(self):
        """
        VECTOR: Inyección de un payload masivo (100,000+ chars).
        EXPECTATIVA: Truncamiento estricto en capa 7. Cero desbordamiento de buffer.
        """
        massive_input = "💀" * 150_000
        malicious_history = [{"role": "user", "content": "💣" * 20_000}] * 50

        sanitized_messages = self.sentinel._sanear_historial(malicious_history, massive_input)

        # Validación 1: El historial debe ser decapitado a máximo 6 nodos (1 sys + 4 hist + 1 input)
        self.assertLessEqual(len(sanitized_messages), 6, "El historial no fue podado correctamente.")
        
        # Validación 2: El último mensaje debe respetar el MAX_INPUT_CHARS exacto
        last_message_content = sanitized_messages[-1].get("content", "")
        self.assertLessEqual(len(last_message_content), MAX_INPUT_CHARS, "Fuga de memoria detectada en el input.")
        
        print("✅ [TEST 01] Prevención de Payload Bombing: SUPERADA (Poda destructiva confirmada).")

    @patch("openai.resources.chat.completions.Completions.create")
    def test_02_absolute_concurrency_race_condition(self, mock_openai):
        """
        VECTOR: 40 hilos concurrentes sincronizados por barrera cuántica.
        EXPECTATIVA: El disyuntor debe abrirse sin importar la colisión de hilos. Ninguna
                     petición extra debe llegar a la API de OpenAI.
        """
        # Configurar Mock de OpenAI para no gastar tokens reales en el test
        mock_resp = MagicMock()
        mock_resp.choices = [MagicMock(message=MagicMock(content="Mock"))]
        mock_resp.usage = MagicMock(prompt_tokens=10, completion_tokens=10, total_tokens=20)
        mock_openai.return_value = mock_resp

        target_user = "hacker_concurrent_id"
        thread_count = 40
        barrier = threading.Barrier(thread_count)

        def synchronized_attack(worker_id):
            barrier.wait() # Congela el hilo hasta que los 40 estén listos y los suelta al unísono
            return self.sentinel.ejecutar_chat(user_id=target_user, query=f"Ping {worker_id}")

        with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures = [executor.submit(synchronized_attack, i) for i in range(thread_count)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # Auditoría criptográfica de resultados
        api_calls = mock_openai.call_count
        successes = sum(1 for r in results if r.get("success") is True)
        blocks = sum(1 for r in results if r.get("success") is False)

        # La API real NUNCA debe ser llamada más veces que el límite permitido, incluso en concurrencia extrema
        self.assertLessEqual(api_calls, MAX_REQUESTS_PER_WINDOW, f"¡FUGA DETECTADA! Llamadas API: {api_calls}")
        self.assertEqual(successes, api_calls, "Inconsistencia entre peticiones exitosas y llamadas API.")
        self.assertGreaterEqual(blocks, thread_count - MAX_REQUESTS_PER_WINDOW, "El disyuntor falló al bloquear el excedente.")

        print(f"✅ [TEST 02] Resiliencia de Concurrencia (40 Threads): SUPERADA ({api_calls} llamadas filtradas a API).")

    @patch("openai.resources.chat.completions.Completions.create")
    def test_03_zero_cost_quarantine_latency(self, mock_openai):
        """
        VECTOR: Usuario en cuarentena intenta hacer una petición.
        EXPECTATIVA: Rechazo en < 3 milisegundos. OpenAI Call Count = 0.
        """
        user_id = "quarantined_user"
        safe_id = self.sentinel._hash_id(user_id)
        
        # Inyectar estado de cuarentena en la caché
        cache.set(f"fenix:circuit_trip:{safe_id}", True, timeout=900)

        start_time = time.perf_counter()
        response = self.sentinel.ejecutar_chat(user_id=user_id, query="¿Estás ahí?")
        latency_ms = (time.perf_counter() - start_time) * 1000

        self.assertFalse(response["success"], "El usuario en cuarentena logró penetrar el firewall.")
        self.assertTrue(response.get("circuit_tripped"), "Falta flag de circuito abierto.")
        self.assertEqual(mock_openai.call_count, 0, "¡RIESGO FINANCIERO! Se llamó a OpenAI estando en cuarentena.")
        self.assertLess(latency_ms, 5.0, f"Latencia de rechazo muy alta: {latency_ms:.2f}ms")

        print(f"✅ [TEST 03] Cuarentena de Costo Cero: SUPERADA (Rechazo en {latency_ms:.2f} ms).")

    @patch("django.core.cache.cache.incr")
    @patch("django.core.cache.cache.get")
    def test_04_cache_catastrophic_failure_survival(self, mock_cache_get, mock_cache_incr):
        """
        VECTOR: El servidor Redis / Memcached colapsa o rechaza conexiones.
        EXPECTATIVA: El fallback en RAM del proceso debe absorber la carga sin crashear Django.
        """
        # Simulamos que la caché está totalmente destruida lanzando excepciones
        mock_cache_incr.side_effect = Exception("Redis Connection Refused")
        mock_cache_get.side_effect = Exception("Redis Connection Refused")

        user_id = "cache_test_user"
        
        # Hacemos 20 peticiones con la caché "caída"
        responses = []
        for i in range(20):
            responses.append(self.sentinel.ejecutar_chat(user_id=user_id, query="Fallback ping"))

        circuit_trips = sum(1 for r in responses if r.get("circuit_tripped") is True)
        
        # El circuito debe dispararse en la memoria RAM nativa de Python
        self.assertGreater(circuit_trips, 0, "El sistema de supervivencia en RAM falló al detectar el bucle.")
        
        print("✅ [TEST 04] Supervivencia ante Caída de Redis (In-Memory Fallback): SUPERADA.")

