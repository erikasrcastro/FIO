"""Static security assertions on published Worker source; not a dynamic pentest."""
from pathlib import Path
import ast

ROOT=Path(__file__).resolve().parents[1]
WORKER=(ROOT / "worker.py").read_text("utf-8")
WRANGLER=(ROOT / "wrangler.toml").read_text("utf-8")

def test_rate_limit_binding_required_by_code():
    assert 'name = "FIO_GROQ_RATE"' in WRANGLER
    assert "limit = 5" in WRANGLER and "period = 60" in WRANGLER
    assert "await guard_paid_model(" in WORKER
    assert WORKER.index("await guard_paid_model(") < WORKER.index("await process_chat(") if "await process_chat(" in WORKER else WORKER.index("await guard_paid_model(") < WORKER.index("result, observed = await process_chat(")

def test_analytics_point_excludes_secrets_and_messages():
    # Runtime function imports a Cloudflare-only module; inspect AST without importing.
    tree=ast.parse(WORKER)
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="usage_point")
    src=ast.get_source_segment(WORKER,fn)
    for forbidden in ('request.headers','message =','GROQ_API_KEY','FIO_DEMO_ACCESS_KEY','trace_id'):
        assert forbidden not in src

def test_no_uncapped_api_output():
    live=(ROOT / "fio" / "live_api.py").read_text("utf-8")
    assert "MAX_GROQ_BODY" in live
    assert "parse_groq_completion" in live

def test_mock_still_available():
    assert '"mock"' in (ROOT / "fio" / "worker_runtime.py").read_text("utf-8")

def test_deploy_does_not_require_analytics_engine_activation():
    # The prior Cloudflare deployment failed with 10089: Analytics Engine
    # disabled on this Free account. Worker Logs are the safe default.
    assert "[[analytics_engine_datasets]]" not in WRANGLER
    assert "[observability]" in WRANGLER
    assert "enabled = true" in WRANGLER
    assert "name = \"FIO_GROQ_RATE\"" in WRANGLER

def test_health_describes_actual_metrics_backend():
    assert '"metrics_backend": "workers_logs"' in WORKER
    assert '"usage_analytics": "configured"' in WORKER

def test_diagnostic_endpoint_not_exposed_after_retirement():
    assert 'if path == "/api/diagnostics/rate-limit":' not in WORKER
    assert 'from fio.rate_diagnostic import' not in WORKER
    assert '"rate_diagnostic": "retired"' in WORKER
    assert 'if path != "/api/chat":' in WORKER
    assert 'VERSION = "fio-worker-mvp-0.5.4"' in WORKER

def test_diagnostic_uses_existing_binding_only():
    from fio.rate_diagnostic import DIAGNOSTIC_LIMIT_KEY
    from fio.worker_runtime import GROQ_LIMIT_KEY
    assert DIAGNOSTIC_LIMIT_KEY != GROQ_LIMIT_KEY
    assert WRANGLER.count('[[ratelimits]]') == 1
