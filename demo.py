from fio import FIOAgent

fio = FIOAgent()
fio.configurar_contexto(
    tarefa="apresentação da pesquisa",
    ponto_parada="slide 6, seção de resultados",
    proximo_passo_confirmado="escrever uma frase com o resultado principal",
)
for fala in [
    "Putz, a ração acabou! Perdi o fio.",
    "Mude para Leve e me ajuda a retomar.",
    "Agora mude para Full, sem reiniciar. Me ajuda a retomar.",
    "Deixa esse relatório para depois, a escola ligou.",
]:
    r = fio.responder(fala)
    print(f"\nUSUÁRIO: {fala}\nFIO [{r.decisao}]: {r.resposta}")
