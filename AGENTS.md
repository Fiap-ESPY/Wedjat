# Instruções para agentes — Wedjat

## Acompanhamento

Registre backlog, andamento e conclusão exclusivamente em `TODO.md`; não crie tickets separados. Use `[ ]`, `[~]`, `[x]` e `[!]` conforme a legenda do arquivo. Adicione critérios verificáveis à Sprint correspondente e registre bloqueios no próprio item. Se um skill pedir ticket, consulte ou atualize `TODO.md`.

## Triagem

Use `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human` e `wontfix` ao lado do item em `TODO.md` quando a classificação ajudar a explicar o estado da tarefa.

## Domínio

Consulte `CONTEXT.md` antes de explorar ou alterar o modelo de domínio. Use os termos definidos ali e evite os sinônimos explicitamente rejeitados. Se houver uma decisão arquitetural em `docs/adr/`, sinalize qualquer contradição antes de alterá-la.

## Skills de engenharia

As skills de `mattpocock/skills` estão em `.agents/skills/`. Use `.agents/skills/wedjat-matt-orchestrator/SKILL.md` para escolher o fluxo adequado ao trabalho no Wedjat; as instruções acima prevalecem sobre convenções de rastreador, documentação e delegação das skills originais.
