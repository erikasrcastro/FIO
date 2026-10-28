from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, field_validator


class Modo(str, Enum):
    FULL = "full"
    LEVE = "leve"


class Intencao(str, Enum):
    RETOMAR = "retomar"
    MUDAR_MODO = "mudar_modo"
    MUDAR_PRIORIDADE = "mudar_prioridade"
    INFORMAR_CONTEXTO = "informar_contexto"
    PEDIR_DIAGNOSTICO = "pedir_diagnostico"
    PEDIR_VIGILANCIA = "pedir_vigilancia"
    DESCONHECIDA = "desconhecida"


class Contexto(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    tarefa: str | None = None
    ponto_parada: str | None = None
    proximo_passo_confirmado: str | None = None
    modo: Modo = Modo.FULL

    @field_validator("tarefa", "ponto_parada", "proximo_passo_confirmado")
    @classmethod
    def impedir_texto_vazio(cls, v: str | None) -> str | None:
        if v == "":
            return None
        return v


class Percepcao(BaseModel):
    """Saída estrutural de uma IA ou de um mock, nunca autorização de ação."""
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    intencao: Intencao
    modo_solicitado: Modo | None = None
    confianca: float = Field(ge=0, le=1)
    justificativa_curta: str = Field(max_length=240, default="")


class Resultado(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decisao: str
    resposta: str
    modo: Modo
    aviso: str | None = None
    usou_llm: bool = False
