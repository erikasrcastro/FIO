# Segurança e privacidade

- Nunca envie chaves de API, tokens, dados pessoais ou registros privados para o repositório.
- A versão acadêmica mantém o contexto apenas na instância em memória; não declara memória permanente.
- A saída da LLM é validada e não autoriza operações externas automaticamente.
- A consulta BrasilAPI usa somente um ano em HTTPS; não envia mensagens do usuário.
- Dados da API externa são tratados como informação não confiável, não como instruções.
- Antes de divulgar uma demo pública: rate limiting, orçamento de uso da LLM, proteção contra abuso, política de retenção de logs e higienização de traces.
- Relate vulnerabilidades privadamente ao mantenedor; não publique segredos nem dados identificáveis em issues.
