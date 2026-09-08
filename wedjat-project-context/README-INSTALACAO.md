# Instalar a skill do Wedjat no Codex / VS Code

Este pacote já contém a estrutura:

```text
.agents/
└── skills/
    └── wedjat-project-context/
        ├── SKILL.md
        ├── agents/
        │   └── openai.yaml
        └── references/
            ├── project-context.md
            └── sprint-3-data-science.md
```

## Opção recomendada — skill local do repositório

Extraia o ZIP **na raiz do repositório Wedjat**.

Depois a raiz deverá conter:

```text
Wedjat/
├── .agents/
│   └── skills/
│       └── wedjat-project-context/
│           └── SKILL.md
├── ...
```

Abra ou reinicie o Codex no projeto.

A skill deve aparecer como:

`wedjat-project-context`

Você pode invocá-la explicitamente no Codex com:

```text
$wedjat-project-context
```

Exemplos:

```text
$wedjat-project-context analise onde paramos no pipeline de classificação e me diga o próximo passo
```

```text
$wedjat-project-context implemente o baseline TF-IDF + Logistic Regression para comparar com o BERTimbau
```

```text
$wedjat-project-context verifique se nosso split atual tem vazamento entre chunks da mesma reunião
```

## PowerShell

Se o ZIP estiver na pasta Downloads, você também pode extrair e copiar a pasta `.agents` manualmente para a raiz do Wedjat.

Não coloque dados reais sensíveis de transcrições dentro da própria skill. A skill deve guardar contexto e regras; os dados continuam no projeto/ambiente apropriado.
