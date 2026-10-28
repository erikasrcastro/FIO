# Cloudflare Workers — conexão do FIO

**Estado em 28/10/2026:** repositório preparado; Worker e segredos ainda não configurados. A integração real com Groq/BrasilAPI e o deploy público não foram verificados.

## Responsabilidades

- GitHub: código, documentação, CI de testes. Não armazena chaves reais.
- Cloudflare: executa o Worker Python, gerencia `GROQ_API_KEY` como Secret, hospeda a demo.
- Groq: fornece serviço de modelo LLM; chave exclusiva de backend.
- BrasilAPI: endpoint público de feriados; não requer credencial neste fluxo.

## Passos de ativação (ação da proprietária no dashboard Cloudflare)

1. Abrir Cloudflare > **Workers & Pages** > **Create application** > **GitHub**.
2. Autorizar o acesso da integração Cloudflare ao repositório `erikasrcastro/FIO` (escopo mínimo possível).
3. Criar um Worker de nome `fio-demo` (nome definitivo deve corresponder ao `name` do Wrangler). **Não habilitar deploy de produção antes da adaptação de runtime e dos guardrails.**
4. Em Worker > **Settings** > **Variables and Secrets** > **Add**, selecionar **Secret** e cadastrar `GROQ_API_KEY`.
5. Nunca colar a chave no chat, README, `.env.example`, GitHub Actions logs ou no JavaScript servido ao navegador.
6. Após adaptação para Cloudflare Python Workers, deploy controlado em `workers.dev` e validação: saúde do serviço, autenticação de origem, resposta Groq real, resposta BrasilAPI real e fallback.
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
