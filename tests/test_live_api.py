"""Groq contract tests; fixtures only, no real external calls."""
import json
import pytest
from fio.live_api import GroqContractError, make_groq_payload, parse_groq_completion, StaticPerceptor
from fio import Contexto, FIOAgent, Modo

def test_groq_request_structure_and_no_secrets():
    payload = make_groq_payload("me perdi", Contexto(tarefa="relatório", ponto_parada="resultados"))
    assert payload["model"] == "openai/gpt-oss-20b"
    assert payload["response_format"]["type"] == "json_object"
    assert payload["messages"][0]["role"] == "system"
    assert "me perdi" in payload["messages"][1]["content"]
    assert "Authorization" not in json.dumps(payload)

def test_valid_response_can_drive_decision():
    raw = json.dumps({"choices":[{"message":{"content":json.dumps({
        "intencao":"retomar", "confianca":0.95, "modo_solicitado":None, "justificativa_curta":"retomada"})}}]})
    p = parse_groq_completion(raw)
    agent = FIOAgent(perceptor=StaticPerceptor(p),
        contexto=Contexto(tarefa="relatório",ponto_parada="resultados",
                         proximo_passo_confirmado="escrever uma frase"))
    result = agent.responder("Me ajuda a retomar")
    assert result.decisao == "orientar_full"
    assert result.modo == Modo.FULL

@pytest.mark.parametrize("body", ["{}", "{invalid", "", "[]",
    json.dumps({"choices":[{"message":{"content":'{"intencao":"injetar","confianca":0.9}'}}]})])
def test_reject_invalid_completion(body):
    with pytest.raises(GroqContractError):
        parse_groq_completion(body)

def test_model_cannot_force_malicious_actions():
    raw = json.dumps({"choices":[{"message":{"content":json.dumps({
        "intencao":"retomar","confianca":0.99,"extra":"drop-all"})}}]})
    with pytest.raises(GroqContractError):
        parse_groq_completion(raw)

def test_groq_token_accounting_from_provider():
    from fio.live_api import extract_groq_usage
    assert extract_groq_usage(json.dumps({"usage":{"prompt_tokens":125,
        "completion_tokens":43, "total_tokens":168}})) == {
        "prompt_tokens":125, "completion_tokens":43, "total_tokens":168}


@pytest.mark.parametrize("usage", [
    {"prompt_tokens":-2, "completion_tokens":1000001, "total_tokens":True},
    {"prompt_tokens":"200", "completion_tokens":1.4, "total_tokens":None},
    None,
])
def test_groq_usage_invalid_values_are_not_logged_as_counts(usage):
    from fio.live_api import extract_groq_usage
    result = extract_groq_usage(json.dumps({"usage":usage}))
    assert result["prompt_tokens"] == 0
    assert result["total_tokens"] == 0
