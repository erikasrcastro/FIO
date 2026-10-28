"""FIO v3 — protótipo acadêmico de decisão controlada."""
from .agent import FIOAgent
from .models import Contexto, Intencao, Modo, Percepcao, Resultado
from .feriados import BrasilAPIFeriados, FalhaServicoExterno, ConsultaFeriado

__all__ = ["FIOAgent", "Contexto", "Intencao", "Modo", "Percepcao", "Resultado", "BrasilAPIFeriados", "FalhaServicoExterno", "ConsultaFeriado"]
