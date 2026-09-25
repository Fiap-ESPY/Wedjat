---
name: wedjat-matt-orchestrator
description: Selecionar e combinar as skills de mattpocock/skills instaladas no Wedjat para investigar, planejar, implementar ou revisar trabalho de engenharia, respeitando TODO.md e CONTEXT.md.
---

# Orquestrador das skills do Matt no Wedjat

Use este roteador quando o pedido envolver um fluxo de engenharia e a pessoa não tiver indicado uma skill específica. As skills originais estão em `../<nome>/SKILL.md`. Leia somente as que forem necessárias para o trabalho atual. Se a pessoa indicar uma skill, priorize a indicada.

## Contexto obrigatório

- Leia `AGENTS.md` e `CONTEXT.md` antes de explorar ou alterar o domínio. Confira `docs/adr/` quando existir.
- Registre backlog, critérios verificáveis, andamento e bloqueios somente na Sprint correspondente de `TODO.md`. Qualquer instrução das skills originais para criar issue, ticket, arquivo em `.scratch/` ou rastreador externo deve ser adaptada a esse arquivo.
- Preserve os termos de `CONTEXT.md`, a arquitetura notebook-first da Sprint 4 e a fronteira `analisar_transcricao` do notebook 18. Aponte uma contradição com ADR antes de mudar a decisão.
- Não crie agentes paralelos, commits, PRs ou publicações apenas porque uma skill original sugere essas etapas. Faça isso somente quando o pedido ou as instruções aplicáveis autorizarem.

## Escolha do fluxo

1. **Pedido ainda indefinido:** use `grill-with-docs` para decisões que realmente dependem da pessoa; use `domain-modeling` para termos ambíguos. Consulte `grill-me` somente fora de um repositório. Não repita perguntas respondidas em `TODO.md`, `CONTEXT.md` ou no pedido.
2. **Auditoria, lacunas ou diagnóstico:** compare a implementação com os critérios da Sprint em `TODO.md` diretamente. Use `code-review` quando houver um diff e um ponto de comparação definidos; `diagnosing-bugs` quando há uma falha reproduzível; `research` quando uma fonte externa precisa ser verificada. Registre achados e próximos critérios em `TODO.md`.
3. **Plano de trabalho:** use `to-spec` ou `wayfinder` quando houver decisões de escopo ainda abertas; use `to-tickets` apenas para decompor o plano em itens de `TODO.md`, com dependências e critérios verificáveis no próprio item.
4. **Implementação:** use `implement` para executar itens definidos. Aplique `tdd` em comportamentos que precisam de testes e `codebase-design` quando a fronteira entre módulos for parte do problema. Compare o diff com os critérios de `TODO.md` antes de declarar conclusão; use `code-review` somente quando houver ponto de comparação definido e a delegação exigida pela skill for autorizada.
5. **Manutenção ou caso especial:** `improve-codebase-architecture` para levantamento arquitetural; `resolving-merge-conflicts` para conflito existente; `prototype` para pergunta que exige experimento descartável; `triage` para solicitações recebidas sem classificação; `wizard` somente para etapas que exigem atuação humana fora do ambiente.

As demais skills instaladas (`ask-matt`, `setup-matt-pocock-skills`, `grilling`, `handoff`, `teach`, `to-questionnaire`, `wait-what` e `writing-for-agents`) são opcionais para necessidades específicas. `AGENTS.md` já define o rastreador e o vocabulário de triagem; não execute `setup-matt-pocock-skills` para criar outro rastreador.

## Entrega

Execute o trabalho autorizado até um resultado verificável. Ao concluir, informe o que foi feito, quais verificações passaram e quais itens de `TODO.md` continuam pendentes ou bloqueados, sem tratar métricas de pseudo-rótulos como validação humana.
