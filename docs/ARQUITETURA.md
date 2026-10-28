# Arquitetura do FIO

~~~mermaid
flowchart TD
 U[Usuário] --> I[Entrada e contexto]
 I --> P[Percepção: mock ou LLM]
 P --> V[Validação Pydantic]
 V --> D[Decisão em Python]
 D --> A[Uma ação ou pergunta]
 D --> E{Consulta externa explicitamente solicitada?}
 E -->|Sim, data completa| API[BrasilAPI HTTPS]
 API --> V2[Validar resposta externa]
 V2 --> A
 E -->|Não| A
~~~

A IA classifica a intenção; o controlador Python mantém as regras de ação. Nenhum resultado externo modifica prioridades automaticamente. O modo Full dirige a próxima ação; o modo Leve estimula a autonomia. Contexto ausente resulta em esclarecimento, nunca em fabricação de memória.

**Limitação:** estado é somente em memória por instância, sem armazenamento permanente entre sessões. Para Cloudflare será necessária adaptação e testes do runtime e, se desejado, persistência consentida e protegida.
