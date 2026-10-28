"""HTML da demonstração sem bibliotecas frontend ou armazenamento de conversas."""
PAGE = """<!doctype html>
<html lang="pt-BR"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="dark">
<title>FIO — Retome de onde parou</title>
<style>
:root{font-family:Inter,system-ui,-apple-system,Segoe UI,sans-serif;color:#e6edf7;background:#0c111a}
*{box-sizing:border-box}body{margin:0;min-height:100vh;background:radial-gradient(circle at 80% 8%,#10273e 0,transparent 38%),#0c111a}
header,main,footer{max-width:1030px;margin:auto;padding:20px}
header{display:flex;align-items:center;justify-content:space-between;gap:16px;border-bottom:1px solid #283344}
.brand{font-weight:900;font-size:28px;letter-spacing:-1.5px}.brand b{color:#f44c8c}
.subtitle{color:#9caec3;font-size:13px}
h1{font-size:clamp(30px,5vw,50px);line-height:1.13;letter-spacing:-1.5px;margin:14px 0}h1 strong{color:#ff6397}
p{color:#a9b9cd;line-height:1.6}main{padding-top:27px}
.grid{display:grid;grid-template-columns:1.02fr 1fr;gap:22px;margin-top:25px}
.panel{border:1px solid #293a4d;background:#131c2a;border-radius:18px;padding:23px;min-width:0}
.panel h2{font-size:17px;margin:0 0 19px}label{display:block;color:#cbd8e9;font-size:13px;margin:15px 0 6px}
input,textarea,select{width:100%;color:#eaf1ff;background:#091321;border:1px solid #3a5067;padding:11px 13px;border-radius:9px;font:inherit;font-size:14px;resize:vertical}
input:focus,textarea:focus,select:focus{outline:2px solid #f45188;outline-offset:1px}
button{background:#f44c8c;border:0;border-radius:10px;color:#100b14;font-size:14px;font-weight:750;padding:12px 18px;cursor:pointer}
button:disabled{opacity:.65;cursor:wait}
.out{background:#091321;border:1px solid #2f4156;border-radius:12px;padding:17px;min-height:151px;white-space:pre-wrap;line-height:1.58;color:#e6edf7;font-size:15px}
.mini{font-size:12px;color:#91a4bc}.status{margin:12px 0;color:#b7c8da;font-size:13px}
.pills{display:flex;gap:8px;flex-wrap:wrap;margin:14px 0}.pill{border:1px solid #334a60;border-radius:100px;padding:6px 10px;color:#8fa8c3;font-size:12px}
footer{border-top:1px solid #273748;color:#8198b1;font-size:12px;margin-top:30px}
a{color:#ff92b9}code{color:#fec1d6}
@media(max-width:780px){.grid{grid-template-columns:1fr}header{align-items:start;flex-direction:column}}
</style></head>
<body>
<header><div class="brand"><b>F</b>IO<span style="font-size:14px;color:#9fb3c9;font-weight:400"> / seu fio de volta</span></div><div class="subtitle">FIAP · Agentes Inteligentes · Protótipo acadêmico</div></header>
<main><h1>Foi interrompida? <strong>Retome de onde parou.</strong></h1>
<p>O FIO ajuda a reconstruir uma tarefa a partir do contexto que você fornece, oferecendo um passo de cada vez — sem vigilância, cobranças ou promessas falsas de memória.</p>
<div class="pills"><span class="pill">Full ou Leve</span><span class="pill">Contexto explícito</span><span class="pill">Rastreabilidade técnica</span><span class="pill">Sem dados persistidos</span></div>
<div class="grid">
<section class="panel"><h2>Seu ponto de partida</h2>
<form id="form">
<label for="mode">Modo de assistência</label><select id="mode"><option value="full">Full — uma orientação direta</option><option value="leve">Leve — mais autonomia</option></select>
<label for="provider">Motor de interpretação</label>
<select id="provider"><option value="mock">Simulado — acesso livre</option><option value="groq">Groq real — acesso protegido</option></select>
<div id="groqWrap" style="display:none">
<label for="groqCode">Código privado de demonstração</label>
<input id="groqCode" type="password" maxlength="256" autocomplete="off" placeholder="Código fornecido pela responsável pelo FIO">
<p class="mini">No modo Groq, sua mensagem e o contexto fornecido são enviados ao serviço externo de IA. Não inclua dados pessoais ou informações sensíveis. A chave da API fica apenas no servidor.</p>
</div>
<label for="task">Tarefa atual (opcional)</label><input id="task" maxlength="160" placeholder="Ex.: apresentação do meu projeto">
<label for="stop">Onde você parou? (opcional)</label><input id="stop" maxlength="160" placeholder="Ex.: slide 6, seção de resultados">
<label for="step">Próxima ação já definida (opcional)</label><input id="step" maxlength="220" placeholder="Ex.: escrever uma frase com o principal resultado">
<label for="message">O que aconteceu?</label><textarea id="message" required maxlength="900" rows="4" placeholder="Ex.: Me distraí e perdi o fio. Pode me ajudar a retomar?"></textarea>
<div style="margin-top:14px"><button type="submit" id="send">Conversar com o FIO</button></div>
</form></section>
<section class="panel"><h2>Resposta do FIO</h2>
<div class="out" id="answer" aria-live="polite">Preencha a tarefa e escreva sua mensagem, ou peça ajuda sem contexto. O FIO perguntará o que falta.</div>
<div class="status" id="status">Ambiente: modo simulado livre; Groq real disponível somente com código autorizado. Consulta BrasilAPI permitida em pedidos de feriados com data.</div>
<p class="mini">Cada solicitação é independente: os dados informados são reenviados no formulário e não ficam salvos entre sessões. O identificador de rastreamento não contém dados pessoais.</p>
<div class="mini" id="trace"></div>
</section>
</div>
</main><footer>FIO · Projeto acadêmico de Éricka Castro · <a href="https://github.com/erikasrcastro/FIO" rel="noopener noreferrer" target="_blank">Código e documentação no GitHub</a> · <a href="/healthz">Status técnico</a></footer>
<script>
const form = document.getElementById('form');
const providerSel = document.getElementById('provider');
providerSel.addEventListener('change', () => {
  document.getElementById('groqWrap').style.display = providerSel.value === 'groq' ? 'block' : 'none';
});
form.addEventListener('submit', async (ev) => {
  ev.preventDefault(); const btn=document.getElementById('send');
  const out=document.getElementById('answer'); const status=document.getElementById('status');
  btn.disabled=true;out.textContent='Processando sua solicitação…';
  try {
    const payload = {mode:document.getElementById('mode').value,task:document.getElementById('task').value,
      stop_point:document.getElementById('stop').value,next_step:document.getElementById('step').value,
      message:document.getElementById('message').value, provider:providerSel.value};
    const headers={'Content-Type':'application/json'};
    if(providerSel.value === 'groq') headers['X-FIO-Demo-Key']=document.getElementById('groqCode').value;
    const r=await fetch('/api/chat',{method:'POST',headers:headers,body:JSON.stringify(payload)});
    const data=await r.json();
    if(!r.ok)throw new Error(data.error || 'Não foi possível concluir a solicitação.');
    out.textContent=data.response;
    status.textContent='Decisão: '+data.decision+' · Modo: '+data.mode+' · Interpretação: '+data.perception+' · API de dados: '+(data.integration==='none'?'nenhuma':data.integration);
    document.getElementById('trace').textContent='Trace ID: '+data.trace_id;
  } catch(e){out.textContent='Ocorreu um erro: '+e.message;status.textContent='Falha tratada; tente novamente.'}
  finally{btn.disabled=false}
});
</script></body></html>"""
