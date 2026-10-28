"""Controlador determinístico: percepção -> validação -> decisão -> ação."""
from .models import Contexto, Intencao, Modo, Percepcao, Resultado
from .feriados import BrasilAPIFeriados, FalhaServicoExterno
from .perception import MockPerceptor, Perceptor, GroqPerceptor, normalizar
import re
from datetime import datetime


class FIOAgent:
    def __init__(self, perceptor: Perceptor | None = None, contexto: Contexto | None = None,
                 servico_feriados: BrasilAPIFeriados | None = None):
        self.perceptor = perceptor or MockPerceptor()
        self.contexto = contexto.model_copy(deep=True) if contexto else Contexto()
        self.servico_feriados = servico_feriados or BrasilAPIFeriados()

    def configurar_contexto(self, tarefa: str, ponto_parada: str | None = None,
                            proximo_passo_confirmado: str | None = None) -> None:
        self.contexto.tarefa = tarefa
        self.contexto.ponto_parada = ponto_parada
        self.contexto.proximo_passo_confirmado = proximo_passo_confirmado

    def _resultado(self, decisao: str, resposta: str, aviso: str | None = None) -> Resultado:
        return Resultado(decisao=decisao, resposta=resposta, modo=self.contexto.modo,
                         aviso=aviso, usou_llm=isinstance(self.perceptor, GroqPerceptor))

    def _retomar(self) -> Resultado:
        c = self.contexto
        if not c.tarefa:
            return self._resultado("pedir_contexto", "Qual tarefa você quer retomar?")
        if not c.ponto_parada:
            return self._resultado("pedir_ponto", f"Em que parte de {c.tarefa} você parou?")
        if not c.proximo_passo_confirmado:
            return self._resultado("pedir_proximo_passo", f"Você estava em {c.ponto_parada}. Qual era a próxima ação concreta prevista nessa parte?")
        if c.modo == Modo.FULL:
            return self._resultado("orientar_full", f"Você estava em {c.ponto_parada}. Próxima ação: {c.proximo_passo_confirmado}.")
        return self._resultado("orientar_leve", f"Você estava em {c.ponto_parada}. Para começar a ação '{c.proximo_passo_confirmado}', qual é o menor movimento que você consegue fazer agora?")

    def responder(self, mensagem: str) -> Resultado:
        if not mensagem or not mensagem.strip():
            return self._resultado("pedir_mensagem", "O que você gostaria de retomar?")
        t = normalizar(mensagem)
        if any(x in t for x in ["diagnosticar", "me diagnost", "tenho tdah?"]):
            return self._resultado("limite_clinico", "Não posso fazer diagnósticos. Uma avaliação clínica exige um profissional habilitado. Posso ajudar a retomar uma tarefa.")
        if any(x in t for x in ["me esculach", "me puna", "me vigie", "me fiscalize", "me punir", "vigiar tudo"]):
            return self._resultado("limite_vigilancia", "Não monitoro suas atividades nem aplico punições. Posso ajudar a retomar uma tarefa, se você desejar.")
        if re.search(r"\bferiad[oa]s?\b", t):
            datas = re.findall(r"(?<!\d)(\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})(?!\d)", mensagem)
            if not datas:
                return self._resultado("pedir_data_feriado", "Qual data completa você quer conferir (DD/MM/AAAA)?")
            try:
                data = datetime.strptime(datas[0], "%d/%m/%Y" if "/" in datas[0] else "%Y-%m-%d").date()
            except ValueError:
                return self._resultado("data_invalida", "Essa data não é válida. Qual é a data correta (DD/MM/AAAA)?")
            try:
                checagem = self.servico_feriados.consultar(data)
            except FalhaServicoExterno:
                return self._resultado("falha_api_feriados", "Não consegui verificar os feriados agora. Confira o calendário oficial antes de decidir a data.",
                                       "Falha de integração; não foi inventado um resultado")
            data_br = data.strftime("%d/%m/%Y")
            if checagem.feriado_nacional:
                return self._resultado("feriado_confirmado", f"Segundo a BrasilAPI, {data_br} consta como feriado nacional: {checagem.nome}. Para planejar a retomada, você prefere manter ou rever essa data?")
            return self._resultado("sem_feriado_nacional", f"Segundo a BrasilAPI, {data_br} não consta como feriado nacional. Isso não descarta feriados estaduais, municipais ou pontos facultativos.")
        try:
            p = self.perceptor.perceber(mensagem, self.contexto)
            p = Percepcao.model_validate(p)
        except (ValueError, KeyError, TypeError, RuntimeError, TimeoutError, OSError):
            return self._resultado("falha_percepcao", "Não consegui interpretar seu pedido com segurança. Você quer retomar uma tarefa ou mudar de prioridade?", "Falha de interpretação; nenhuma ação externa executada")
        if p.confianca < 0.60:
            return self._resultado("esclarecer", "Você quer retomar uma tarefa ou mudar de prioridade?")
        if p.intencao == Intencao.PEDIR_DIAGNOSTICO:
            return self._resultado("limite_clinico", "Não posso fazer diagnósticos. Para isso, procure um profissional habilitado.")
        if p.intencao == Intencao.PEDIR_VIGILANCIA:
            return self._resultado("limite_vigilancia", "Não monitoro atividades nem aplico punições. Posso ajudar em uma retomada voluntária.")
        if p.intencao == Intencao.MUDAR_PRIORIDADE:
            return self._resultado("respeitar_prioridade", "Entendido. Não vou insistir na tarefa anterior. Se quiser retomá-la durante esta conversa, podemos usar o contexto disponível aqui.")
        if p.intencao == Intencao.MUDAR_MODO:
            if p.modo_solicitado is None:
                return self._resultado("perguntar_modo", "Você prefere o modo Full (orientação direta) ou Leve (mais autonomia)?")
            self.contexto.modo = p.modo_solicitado
            if any(s in t for s in ["retom", "voltar", "continua", "sem reiniciar"]):
                return self._retomar()
            return self._resultado("confirmar_modo", f"Modo {self.contexto.modo.value} selecionado nesta conversa.")
        if p.intencao == Intencao.RETOMAR:
            return self._retomar()
        return self._resultado("esclarecer", "Você quer retomar uma tarefa ou mudar de prioridade?")
