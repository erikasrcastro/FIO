"""Demonstração OFFLINE: serviço externo simulado, respostas de exemplo."""
import json
from fio import FIOAgent, BrasilAPIFeriados

fixture = [{"date": "2026-11-20", "name": "Dia Nacional de Zumbi e da Consciência Negra", "type": "national"}]
service = BrasilAPIFeriados(transport=lambda *_: json.dumps(fixture).encode())
agent = FIOAgent(servico_feriados=service)
for entrada in [
    "Meu projeto ficou parado, perdi o fio.",
    "20/11/2026 é feriado? Queria retomar nesse dia.",
    "Me ajuda a retomar o projeto",
]:
    out = agent.responder(entrada)
    print(f"USUÁRIO: {entrada}\nFIO [{out.decisao}]: {out.resposta}\n")
