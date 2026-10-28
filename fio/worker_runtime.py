"""Request-independent application logic with injected async network transport.

Never persist or log user input in this module.
"""
from __future__ import annotations
import re
import json
import secrets
from datetime import datetime
from typing import Callable, Awaitable
from .agent import FIOAgent
from .feriados import BrasilAPIFeriados, FalhaServicoExterno, BASE_URL
from .models import Contexto
from .perception import normalizar
from .live_api import GROQ_ENDPOINT, make_groq_payload, parse_groq_completion, StaticPerceptor, GroqContractError

HttpTransport = Callable[[str, str, dict, str | None, int], Awaitable[tuple[int, str]]]

class RequestRejected(Exception):
    def __init__(self, status: int, code: str, description: str):
        super().__init__(description)
        self.status = status
        self.code = code
        self.description = description

def demo_credential_authorized(expected: str, supplied: str) -> bool:
    return (isinstance(expected, str) and isinstance(supplied, str) and
            24 <= len(expected) <= 256 and 24 <= len(supplied) <= 256 and
            secrets.compare_digest(expected, supplied))

def _holiday_date(message: str):
    matches = re.findall(r"(?<!\d)(\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})(?!\d)", message)
    if not matches:
        return None
    try:
        return datetime.strptime(matches[0], "%d/%m/%Y" if "/" in matches[0] else "%Y-%m-%d").date()
    except ValueError:
        return None

def is_rule_only(message: str) -> bool:
    t = normalizar(message)
    return bool(re.search(r"\bferiad[oa]s?\b", t)) or any(x in t for x in [
        "diagnosticar", "me diagnost", "tenho tdah?", "me esculach", "me puna",
        "me vigie", "me fiscalize", "me punir", "vigiar tudo",
    ])

async def process_chat(message: str, context: Contexto, provider: str,
                       supplied_code: str, groq_api_key: str, demo_code: str,
                       transport: HttpTransport) -> tuple[dict, dict]:
    if provider not in ("mock", "groq"):
        raise RequestRejected(400, "provider_invalid", "Tipo de interpretação inválido")
    if provider == "groq":
        if not groq_api_key or not demo_credential_authorized(demo_code, supplied_code):
            raise RequestRejected(403, "demo_access_denied", "Demonstração Groq não autorizada; use o modo simulado")

    integration = "none"
    llm_used = False
    service_status = None
    perception = "mock" if provider == "mock" else "rule"

    if re.search(r"\bferiad[oa]s?\b", normalizar(message)):
        dt = _holiday_date(message)
        if dt and 1900 <= dt.year <= 2199:
            integration = "brasilapi"
            url = f"{BASE_URL}/{dt.year}"
            try:
                service_status, raw = await transport(url, "GET", {"Accept": "application/json"}, None, 8000)
                if service_status != 200 or len(raw.encode("utf-8")) > 256000:
                    raise FalhaServicoExterno("status or payload limit")
                service = BrasilAPIFeriados(transport=lambda *_: raw.encode("utf-8"))
                result = FIOAgent(contexto=context, servico_feriados=service).responder(message)
            except Exception:
                result = FIOAgent(contexto=context, servico_feriados=BrasilAPIFeriados(
                    transport=lambda *_: (_ for _ in ()).throw(FalhaServicoExterno("external unavailable")))).responder(message)
                integration = "brasilapi_fallback"
        else:
            result = FIOAgent(contexto=context).responder(message)
        perception = "rule"
    elif provider == "groq" and not is_rule_only(message):
        try:
            payload = json.dumps(make_groq_payload(message, context), ensure_ascii=False)
            service_status, raw = await transport(GROQ_ENDPOINT, "POST", {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {groq_api_key}",
            }, payload, 12000)
            if service_status != 200:
                raise RequestRejected(502, "groq_upstream_error", "Groq indisponível; tente novamente")
            perceived = parse_groq_completion(raw)
            result = FIOAgent(contexto=context, perceptor=StaticPerceptor(perceived)).responder(message)
            llm_used = True
            perception = "groq"
        except RequestRejected:
            raise
        except (ValueError, GroqContractError, TypeError, TimeoutError, OSError):
            raise RequestRejected(502, "groq_invalid_result", "Falha na interpretação pelo Groq; nenhuma ação externa foi executada") from None
    else:
        result = FIOAgent(contexto=context).responder(message)

    response = {"response": result.resposta, "decision": result.decisao,
                "mode": result.modo.value, "perception": perception,
                "integration": integration}
    telemetry = {"decision": result.decisao, "perception": perception,
                 "integration": integration, "llm_used": llm_used,
                 "provider_status": service_status}
    return response, telemetry
