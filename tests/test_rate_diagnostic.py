"""Ensaios offline: segurança e isolamento do diagnóstico SEC-053."""
import asyncio
import pytest
from fio.rate_diagnostic import run_rate_diagnostic, DIAGNOSTIC_LIMIT_KEY
from fio.worker_runtime import GROQ_LIMIT_KEY, RequestRejected

VALID = "demo-key-synthetic-with-more-than-24-chars"

def attempt(supplied=VALID, expected=VALID, permit=None):
    return asyncio.run(run_rate_diagnostic(expected, supplied, permit))

def test_auth_failure_prevents_any_rate_check():
    calls = []
    async def forbidden(bucket):
        calls.append(bucket)
        return True
    with pytest.raises(RequestRejected) as e:
        attempt(supplied="wrong", permit=forbidden)
    assert e.value.status == 403
    assert e.value.code == "diagnostic_access_denied"
    assert calls == []

def test_missing_secret_prevents_any_rate_check():
    calls = []
    async def forbidden(bucket):
        calls.append(bucket)
        return True
    with pytest.raises(RequestRejected) as e:
        attempt(expected="", permit=forbidden)
    assert e.value.status == 403 and calls == []

def test_uses_isolated_nonsecret_bucket():
    calls = []
    async def allow(bucket):
        calls.append(bucket)
        return True
    status, obj = attempt(permit=allow)
    assert status == 200 and obj["code"] == "diagnostic_allowed"
    assert obj["groq_called"] is False
    assert calls == [DIAGNOSTIC_LIMIT_KEY]
    assert DIAGNOSTIC_LIMIT_KEY != GROQ_LIMIT_KEY
    assert VALID not in DIAGNOSTIC_LIMIT_KEY

def test_native_denial_returns_429_without_model_call():
    async def deny(bucket):
        return False
    status, obj = attempt(permit=deny)
    assert status == 429
    assert obj["code"] == "diagnostic_rate_limited"
    assert obj["groq_called"] is False

def test_missing_binding_fails_closed():
    with pytest.raises(RequestRejected) as e:
        attempt(permit=None)
    assert e.value.status == 503

def test_binding_exception_fails_closed_without_leaking_detail():
    async def broken(bucket):
        raise RuntimeError("secret-diagnostic-internal-info")
    with pytest.raises(RequestRejected) as e:
        attempt(permit=broken)
    assert e.value.code == "diagnostic_binding_unavailable"
    assert "secret-diagnostic-internal-info" not in e.value.description

@pytest.mark.parametrize("invalid", ["yes", 1, None, {"success":True}])
def test_invalid_binding_response_is_rejected(invalid):
    async def broken(bucket):
        return invalid
    with pytest.raises(RequestRejected) as e:
        attempt(permit=broken)
    assert e.value.status == 503 and e.value.code == "diagnostic_binding_invalid"

def test_response_has_no_credentials_or_user_information():
    async def allow(bucket):
        return True
    _, obj=attempt(permit=allow)
    assert set(obj)=={"ok","code","binding","bucket","groq_called"}
    assert VALID not in str(obj)
