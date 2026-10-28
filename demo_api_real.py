"""Demonstração ONLINE: chamada HTTPS real à BrasilAPI. Requer acesso à rede."""
from fio import FIOAgent

agent = FIOAgent()
saida = agent.responder("20/11/2026 é feriado?")
print(f"Decisão: {saida.decisao}\nResposta: {saida.resposta}\nAviso: {saida.aviso}")
