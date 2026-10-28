"""FIO Cloudflare Worker: HTML, backend, Groq gated API and BrasilAPI live.

No conversations or secret values are logged. Requests have no durable memory.
"""
import json
import time
import uuid
from urllib.parse import urlparse
from workers import WorkerEntrypoint, Response

from fio import FIOAgent, Contexto, Modo
from fio.worker_runtime import process_chat, RequestRejected, guard_paid_model
from web_ui import PAGE

MAX_REQUEST_BYTES = 4096
VERSION = "fio-worker-mvp-0.5.2"


def json_response(data: dict, status: int = 200):
    return Response(
        json.dumps(data, ensure_ascii=False),
        status=status,
        headers={"Content-Type": "application/json; charset=utf-8",
                 "Cache-Control": "no-store",
                 "X-Content-Type-Options": "nosniff"}
    )



async def transport_http(url: str, method: str, headers: dict, body: str | None, timeout_ms: int):
    """Cloudflare's native async fetch, not urllib.request (unsupported in Workers)."""
    from js import fetch as js_fetch, Object, AbortSignal
    from pyodide.ffi import to_js
    options = to_js({"method": method, "headers": headers}, dict_converter=Object.fromEntries)
    if body is not None:
        options.body = body
    options.signal = AbortSignal.timeout(timeout_ms)
    response = await js_fetch(url, options)
    text = str(await response.text())
    return int(response.status), text



async def limiter_allow(env, key: str) -> bool:
    """Bridge to Cloudflare native, local/approximate rate limiting binding."""
    from js import Object
    from pyodide.ffi import to_js
    binding = getattr(env, "FIO_GROQ_RATE", None)
    if binding is None:
        raise RuntimeError("missing rate limiter binding")
    options = to_js({"key": key}, dict_converter=Object.fromEntries)
    result = await binding.limit(options)
    return bool(result.success)


def usage_point(decision: str, status: int, event: dict, duration_ms: float) -> dict:
    """No messages, response text, IP, secret, or trace ID in analytics."""
    decisions = {"orientar_full", "orientar_leve", "orientar_full_sem_passo",
                 "orientar_leve_sem_passo", "feriado_confirmado",
                 "falha_api_feriados", "groq_rate_limited", "demo_access_denied",
                 "rate_limit_unavailable", "rate_limit_invalid", "groq_upstream_error",
                 "groq_invalid_result", "limite_vigilancia", "limite_clinico",
                 "validation_error", "internal_error"}
    safe_decision = decision if decision in decisions else "other"
    interpretation = event.get("perception", "none")
    if interpretation not in ("mock", "groq", "rule", "none"):
        interpretation = "none"
    external = event.get("integration", "none")
    if external not in ("none", "brasilapi", "brasilapi_fallback"):
        external = "none"
    numbers = []
    for name in ("prompt_tokens", "completion_tokens", "total_tokens"):
        val = event.get(name, 0)
        numbers.append(float(val) if type(val) is int and 0 <= val <= 1_000_000 else 0.0)
    return {
        "blobs": ["api_chat", safe_decision, str(int(status)), interpretation, external],
        "doubles": [1.0, max(0.0, round(duration_ms, 2)), *numbers],
        "indexes": ["fio"],
    }


def emit_usage_analytics(env, decision: str, status: int, event: dict, duration_ms: float) -> None:
    """Best-effort analytics; must not affect the user's response."""
    from js import Object
    from pyodide.ffi import to_js
    binding = getattr(env, "FIO_ANALYTICS", None)
    if binding is None:
        return
    point = to_js(usage_point(decision, status, event, duration_ms),
                  dict_converter=Object.fromEntries)
    binding.writeDataPoint(point)

def validate_input(body):
    if not isinstance(body, dict):
        raise ValueError("Requisição deve conter um objeto JSON")
    allowed = {"mode", "task", "stop_point", "next_step", "message", "provider"}
    if not set(body).issubset(allowed):
        raise ValueError("Campos desconhecidos")
    msg = body.get("message", "")
    if not isinstance(msg, str) or not msg.strip() or len(msg) > 900:
        raise ValueError("Mensagem deve conter de 1 a 900 caracteres")
    for field, limit in (("task", 160), ("stop_point", 160), ("next_step", 220)):
        v = body.get(field, "")
        if not isinstance(v, str) or len(v) > limit:
            raise ValueError(f"Campo {field} inválido")
    modo = body.get("mode", "full")
    if modo not in ("full", "leve"):
        raise ValueError("Modo deve ser 'full' ou 'leve'")
    provider = body.get("provider", "mock")
    if provider not in ("mock", "groq"):
        raise ValueError("Provedor inválido")
    return msg, Contexto(
        tarefa=body.get("task") or None,
        ponto_parada=body.get("stop_point") or None,
        proximo_passo_confirmado=body.get("next_step") or None,
        modo=Modo(modo),
    ), provider


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        url = urlparse(str(request.url))
        path = url.path
        method = str(request.method).upper()

        if path == "/healthz" and method == "GET":
            from fio.worker_runtime import demo_credential_authorized
            key_present = bool(str(getattr(self.env, "GROQ_API_KEY", "") or ""))
            demo_code = str(getattr(self.env, "FIO_DEMO_ACCESS_KEY", "") or "")
            return json_response({"ok": True, "version": VERSION,
                                  "llm": "protected" if key_present and len(demo_code) >= 24 else "locked",
                                  "session_memory": "none", "external_api": "brasilapi_enabled",
                                  "groq_rate_limit": "configured" if getattr(self.env, "FIO_GROQ_RATE", None) is not None else "unavailable",
                                  "usage_analytics": "configured" if getattr(self.env, "FIO_ANALYTICS", None) is not None else "not_enabled",
                                  "metrics_backend": "workers_logs"})

        if path == "/" and method == "GET":
            return Response(PAGE, headers={
                "Content-Type": "text/html; charset=utf-8",
                "Cache-Control": "no-store",
                "Content-Security-Policy": "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'",
                "X-Content-Type-Options": "nosniff",
                "Referrer-Policy": "no-referrer",
            })

        if path != "/api/chat":
            return json_response({"error": "Rota não encontrada"}, 404)
        if method != "POST":
            return json_response({"error": "Use POST"}, 405)
        if str(request.headers.get("content-type") or "").split(";")[0].strip().lower() != "application/json":
            return json_response({"error": "Content-Type deve ser application/json"}, 415)
        origin = request.headers.get("origin")
        if origin and str(origin).rstrip("/") != f"{url.scheme}://{url.netloc}":
            return json_response({"error": "Origem não autorizada"}, 403)
        try:
            length = int(request.headers.get("content-length") or 0)
            if length > MAX_REQUEST_BYTES:
                return json_response({"error": "Requisição excede o limite"}, 413)
        except (ValueError, TypeError):
            return json_response({"error": "Content-Length inválido"}, 400)

        trace_id = str(uuid.uuid4())
        start = time.monotonic()
        decision = "validation_error"
        status = 400
        event_info = {}
        try:
            # Lê no máximo 4 KB declarados; também verifica conteúdo decodificado.
            raw = await request.text()
            if len(str(raw).encode("utf-8")) > MAX_REQUEST_BYTES:
                return json_response({"error": "Corpo da requisição excede o limite"}, 413)
            msg, context, provider = validate_input(json.loads(str(raw)))
            groq_key = str(getattr(self.env, "GROQ_API_KEY", "") or "")
            demo_code = str(getattr(self.env, "FIO_DEMO_ACCESS_KEY", "") or "")
            supplied_code = str(request.headers.get("x-fio-demo-key") or "")
            # Authorization and quota enforcement BEFORE paid inference.
            async def permit(key):
                return await limiter_allow(self.env, key)
            await guard_paid_model(provider, msg, supplied_code, groq_key,
                                   demo_code, permit)
            result, observed = await process_chat(
                msg, context, provider, supplied_code, groq_key, demo_code, transport_http
            )
            decision = result["decision"]
            event_info = observed
            status = 200
            result["trace_id"] = trace_id
            return json_response(result)
        except RequestRejected as exc:
            decision = exc.code
            status = exc.status
            return json_response({"error": exc.description, "code": exc.code, "trace_id": trace_id}, exc.status)
        except (ValueError, TypeError, json.JSONDecodeError):
            decision = "validation_error"
            status = 400
            return json_response({"error": "Entrada inválida", "trace_id": trace_id}, 400)
        except Exception:
            decision = "internal_error"
            status = 500
            return json_response({"error": "Ocorreu uma falha controlada", "trace_id": trace_id}, 500)
        finally:
            # Somente metadados categóricos, nunca texto, contexto ou credenciais.
            duration_ms = round((time.monotonic() - start) * 1000, 2)
            print(json.dumps({"trace_id": trace_id, "event": "response",
                              "decision": decision, "status": status,
                              "duration_ms": duration_ms,
                              "version": VERSION, "perception": event_info.get("perception", "none"),
                              "external": event_info.get("integration", "none"),
                              "provider_status": event_info.get("provider_status"),
                              "prompt_tokens": event_info.get("prompt_tokens", 0),
                              "completion_tokens": event_info.get("completion_tokens", 0),
                              "total_tokens": event_info.get("total_tokens", 0)}))
            try:
                emit_usage_analytics(self.env, decision, status, event_info, duration_ms)
            except Exception:
                # No secret or exception body is logged. Metrics outage isn't user outage.
                print(json.dumps({"event": "analytics_export_failed", "version": VERSION}))
