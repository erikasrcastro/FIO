"""BrasilAPI: dados externos opcionais para planejamento de retomadas.

Os dados recebidos são informações, nunca instruções de execução.
A única entrada enviada ao provedor é um ano (não há texto do usuário nem dados pessoais).
"""
from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from datetime import date
from typing import Callable
from urllib import error, request
from pydantic import BaseModel, ConfigDict, Field, field_validator

BASE_URL = "https://brasilapi.com.br/api/feriados/v1"
MAX_BYTES = 256_000


class FalhaServicoExterno(Exception):
    """Erro de transporte, formato ou indisponibilidade da API."""


class Feriado(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)
    date: date
    name: str = Field(min_length=1, max_length=200)
    type: str = Field(min_length=1, max_length=60)

    @field_validator("name", mode="before")
    @classmethod
    def evitar_controle_e_instrucao_maliciosa(cls, name: str) -> str:
        if not isinstance(name, str):
            raise ValueError("Nome de feriado inválido")
        if any(ord(c) < 32 for c in name):
            raise ValueError("Nome contém caractere de controle")
        # Defesa conservadora de integridade de exibição: o nome obtido
        # externamente não pode carregar comandos explícitos. Não é um
        # detector genérico de prompt injection nem concede autoridade ao dado.
        plain = unicodedata.normalize("NFKD", name.casefold())
        plain = "".join(c for c in plain if not unicodedata.combining(c))
        if re.search(r"\b(ignore|desconsidere|revele|execute|apague|prompt|token|secret|senha)\b", plain):
            raise ValueError("Nome contém padrão de instrução não confiável")
        return name


class ConsultaFeriado(BaseModel):
    model_config = ConfigDict(extra="forbid")
    data: date
    feriado_nacional: bool
    nome: str | None = None
    fonte: str = BASE_URL


Transport = Callable[[str, float], bytes]


def transporte_padrao(url: str, timeout: float) -> bytes:
    req = request.Request(url, headers={"Accept": "application/json", "User-Agent": "FIO-FIAP-v3.1/1.0"})
    with request.urlopen(req, timeout=timeout) as resp:
        if getattr(resp, "status", 200) != 200:
            raise FalhaServicoExterno(f"HTTP {resp.status}")
        data = resp.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise FalhaServicoExterno("Resposta maior que o limite de segurança")
        return data


@dataclass
class BrasilAPIFeriados:
    timeout: float = 5.0
    transport: Transport = transporte_padrao

    def consultar(self, data: date) -> ConsultaFeriado:
        if not 1900 <= data.year <= 2199:
            raise FalhaServicoExterno("Ano fora da faixa suportada")
        url = f"{BASE_URL}/{data.year}"
        try:
            raw = self.transport(url, self.timeout)
            if not isinstance(raw, bytes) or len(raw) > MAX_BYTES:
                raise ValueError("Payload binário inválido ou excessivo")
            payload = json.loads(raw)
            if not isinstance(payload, list) or len(payload) > 366:
                raise ValueError("Resposta de feriados fora do formato esperado")
            feriados = [Feriado.model_validate(item) for item in payload]
            if any(f.date.year != data.year for f in feriados):
                raise ValueError("A resposta contém datas de outro ano")
            encontrou = next((f for f in feriados if f.date == data), None)
            return ConsultaFeriado(data=data, feriado_nacional=encontrou is not None,
                                   nome=encontrou.name if encontrou else None)
        except (error.URLError, TimeoutError, OSError, ValueError, TypeError, KeyError) as exc:
            raise FalhaServicoExterno(f"Consulta de feriados indisponível ou inválida: {type(exc).__name__}") from exc
