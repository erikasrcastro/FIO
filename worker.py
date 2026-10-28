"""Cloudflare Python Worker — ponto de entrada da demonstração do FIO.

O MVP usa interpretação simulada; nem a credencial Groq nem as mensagens
dos usuários são registradas nos logs. Não há memória entre solicitações.
"""
import json
import time
import uuid
from urllib.parse import urlparse
from workers import WorkerEntrypoint, Response

from fio import FIOAgent, Contexto, Modo
from fio.perception import normalizar
from web_ui import PAGE

MAX_REQUEST_BYTES = 4096
VERSION = "fio-worker-mvp-0.3.2"


def json_response(data: dict, status: int = 200):
    return Response(
        json.dumps(data, ensure_ascii=False),
        status=status,
        headers={"Content-Type": "application/json; charset=utf-8",
                 "Cache-Control": "no-store",
                 "X-Content-Type-Options": "nosniff"}
    )


def validate_input(body):
    if not isinstance(body, dict):
        raise ValueError("Requisição deve conter um objeto JSON")
    allowed = {"mode", "task", "stop_point", "next_step", "message"}
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
    return msg, Contexto(
        tarefa=body.get("task") or None,
        ponto_parada=body.get("stop_point") or None,
        proximo_passo_confirmado=body.get("next_step") or None,
        modo=Modo(modo),
    )


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        url = urlparse(str(request.url))
        path = url.path
        method = str(request.method).upper()

        if path == "/healthz" and method == "GET":
            return json_response({"ok": True, "version": VERSION,
                                  "llm": "not_enabled", "session_memory": "none"})

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
        try:
            # Lê no máximo 4 KB declarados; também verifica conteúdo decodificado.
            raw = await request.text()
            if len(str(raw).encode("utf-8")) > MAX_REQUEST_BYTES:
                return json_response({"error": "Corpo da requisição excede o limite"}, 413)
            msg, context = validate_input(json.loads(str(raw)))
            # A integração BrasilAPI depende de um adaptador HTTP assíncrono;
            # não executamos urllib.request na runtime Pyodide.
            if "feriad" in normalizar(msg):
                decision = "api_pending"
                status = 200
                answer = ("Nesta versão de demonstração a consulta real de feriados ainda não está habilitada. "
                          "A integração será ativada após validação do adaptador HTTP na Cloudflare.")
                return json_response({"response": answer, "decision": decision, "mode": context.modo.value,
                                      "perception": "mock", "trace_id": trace_id})
            agent = FIOAgent(contexto=context)
            result = agent.responder(msg)
            decision = result.decisao
            status = 200
            return json_response({"response": result.resposta, "decision": result.decisao,
                                  "mode": result.modo.value, "perception": "mock",
                                  "trace_id": trace_id})
        except (ValueError, TypeError, json.JSONDecodeError):
            return json_response({"error": "Entrada inválida"}, 400)
        except Exception:
            decision = "internal_error"
            status = 500
            return json_response({"error": "Ocorreu uma falha controlada", "trace_id": trace_id}, 500)
        finally:
            # Somente metadados categóricos, nunca texto, contexto ou credenciais.
            print(json.dumps({"trace_id": trace_id, "event": "response",
                              "decision": decision, "status": status,
                              "duration_ms": round((time.monotonic() - start)*1000, 2),
                              "version": VERSION}))
