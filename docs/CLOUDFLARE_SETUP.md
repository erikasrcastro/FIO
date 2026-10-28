# Cloudflare Workers — conexão do FIO

**Estado em 28/10/2026:** repositório com `worker.py`, `web_ui.py`, `pyproject.toml` e `wrangler.toml`. Worker e segredos ainda não foram confirmados na Cloudflare. Integração real Groq/BrasilAPI no Worker e deploy público permanecem não verificados.

## Responsabilidades

- GitHub: código, documentação, CI de testes. Não armazena chaves reais.
- Cloudflare: executa o Worker Python, gerencia `GROQ_API_KEY` como Secret, hospeda a demo.
- Groq: fornece serviço de modelo LLM; chave exclusiva de backend.
- BrasilAPI: endpoint público de feriados; não requer credencial neste fluxo.

## Passos de ativação (ação da proprietária no dashboard Cloudflare)

1. Abrir Cloudflare > **Workers & Pages** > **Create application** > **GitHub**.
2. Autorizar o acesso da integração Cloudflare ao repositório `erikasrcastro/FIO` (escopo mínimo possível).
3. Criar Worker de nome exato **`fio`** (igual ao `name` em `wrangler.toml`). Deixar **Build command vazio**, definir **Deploy command = `uv run pywrangler deploy`**, **Preview command = `uv run pywrangler preview`** e **Path = `/`**. Para o primeiro deploy, desativar Preview builds. O painel é público se Cloudflare Access estiver desligado. O Worker inicial está em modo mock sem custo de Groq.
4. Depois do primeiro deploy bem-sucedido, em Worker > **Settings** > **Variables and Secrets** > **Add**, cadastrar `GROQ_API_KEY` como **Secret**; **o Worker inicial ainda não faz chamadas Groq**, por segurança. Não ativar inferência real antes dos limites de custo e dos testes.
5. Nunca colar a chave no chat, README, `.env.example`, GitHub Actions logs ou no JavaScript servido ao navegador.
6. Deploy inicial em `workers.dev`, acessar `/healthz` e testar o formulário. Esperado: `llm: not_enabled`. Integração Groq e BrasilAPI **não será afirmada como real no primeiro deploy**.
7. Ativar limites de tráfego/orçamento e logs sanitizados antes de divulgar o link ao professor.

## Atenção ao runtime

O núcleo existente utiliza `urllib.request` e classes Python padrão. A compatibilidade com Cloudflare Python Workers **não está demonstrada**; chamadas de rede podem precisar de adaptadores baseados em `fetch` assíncrono e em bindings. Instalar `workers-py`/`pywrangler`, adicionar `python_workers` no Wrangler e executar testes em `pywrangler dev` antes de produção.

## Configuração segura

- Para desenvolvimento local com Wrangler: usar `.dev.vars` (ignorado no Git) e somente com valores reais na máquina da proprietária.
- Para produção: Cloudflare Secrets, não variáveis de texto puro.
- Para um deploy por Cloudflare Git integration, não precisamos duplicar `GROQ_API_KEY` em GitHub Secrets; só seria necessário um token de deploy do Cloudflare no GitHub se optássemos por GitHub Actions como provedor de deployment.

## Critérios para declarar integração real

Registrar commit SHA, data UTC, domínio real, `trace_id`, status, latência e resultado de chamadas externas. Manter dados pessoais e tokens fora dos logs e evidências públicas.

Documentação oficial: https://developers.cloudflare.com/workers/configuration/secrets/ e https://developers.cloudflare.com/workers/languages/python/ .

## Atenção: validação do primeiro deploy

Se a compilação Pyodide falhar, copie o erro do **Build log**, sem credenciais, e corrija o projeto antes de tentar publicar. O código foi versionado, mas o funcionamento específico no ambiente Cloudflare ainda não foi comprovado por build remoto.

## Troubleshooting de build — 28/10/2026

Falha observada na primeira tentativa: `requirements.txt exists. Delete the file to continue`. O Pywrangler atual exige declarações de dependência em `pyproject.toml`. Correção: arquivo `requirements.txt` retirado do repositório; `pytest` movido para o grupo `dev` de `pyproject.toml`; GitHub Actions passou a instalar/executar via `uv`. A Cloudflare poderá executar o deploy novamente a partir do novo commit. **A correção do código não comprova ainda que o deploy completo esteja funcionando.**
