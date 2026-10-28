"""Demonstração ONLINE do classificador Groq. Não imprime nem grava tokens."""
import os
from fio import FIOAgent
from fio.perception import GroqPerceptor

if not os.environ.get("GROQ_API_KEY"):
    raise SystemExit("GROQ_API_KEY ausente. Configure no ambiente antes de executar; não cole a chave no código.")

fio = FIOAgent(perceptor=GroqPerceptor())
fio.configurar_contexto(tarefa="apresentação da pesquisa", ponto_parada="slide 6, resultados", proximo_passo_confirmado="escrever uma frase com o achado principal")
result = fio.responder("Perdi o fio. Quero retomar.")
print(f"Decisão: {result.decisao}\nResposta: {result.resposta}\nUsou LLM: {result.usou_llm}")
