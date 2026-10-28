"""Diagnóstico autenticado do binding Cloudflare, SEM chamada ao Groq.

A mesma configuração FIO_GROQ_RATE é consultada com uma chave de
contagem independente da chave usada por inferências reais.
"""
from .worker_runtime import RequestRejected, demo_credential_authorized, GROQ_LIMIT_KEY

DIAGNOSTIC_LIMIT_KEY = "fio-rate-diagnostic-v1"
assert DIAGNOSTIC_LIMIT_KEY != GROQ_LIMIT_KEY

async def run_rate_diagnostic(expected_demo_key: str, supplied_demo_key: str, permit_limit):
    """Retorna (HTTP status, payload seguro). Não recebe transporte de API externa."""
    if not demo_credential_authorized(expected_demo_key, supplied_demo_key):
        raise RequestRejected(403, "diagnostic_access_denied", "Acesso ao diagnóstico não autorizado")
    if permit_limit is None:
        raise RequestRejected(503, "diagnostic_binding_unavailable", "Limitador indisponível")
    try:
        allowed = await permit_limit(DIAGNOSTIC_LIMIT_KEY)
    except Exception:
        raise RequestRejected(503, "diagnostic_binding_unavailable", "Limitador indisponível") from None
    if type(allowed) is not bool:
        raise RequestRejected(503, "diagnostic_binding_invalid", "Resposta do limitador inválida")
    return (
        200 if allowed else 429,
        {
            "ok": allowed,
            "code": "diagnostic_allowed" if allowed else "diagnostic_rate_limited",
            "binding": "FIO_GROQ_RATE",
            "bucket": "diagnostic_isolated",
            "groq_called": False,
        }
    )
