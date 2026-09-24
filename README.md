# Wedjat

Wedjat é uma ferramenta de inteligência comercial para analisar transcrições de
reuniões, identificar possíveis oportunidades de negócio e relacionar as
necessidades encontradas com produtos, conceitos e evidências da base de
conhecimento TOTVS.

O projeto combina classificação supervisionada com RAG (*Retrieval-Augmented
Generation*). Atualmente, a saída final é estruturada e fundamentada em fontes;
o sistema ainda não gera respostas livres com um modelo de linguagem.

## O que a ferramenta faz

A versão atual consegue:

- limpar e validar transcrições anonimizadas;
- remover reuniões duplicadas;
- dividir transcrições longas em chunks compatíveis com transformers;
- detectar possíveis oportunidades comerciais em cada chunk;
- agregar os resultados no nível da reunião;
- recuperar produtos, dores, sinais e comparações na base TOTVS;
- devolver nível de evidência, política de uso e URLs das fontes;
- impedir que documentos sem fonte sustentem afirmações factuais;
- manter hipóteses explicitamente separadas de fatos;
- analisar uma nova transcrição com produto, sentimento, risco de churn,
  oportunidade, termos e recomendação sujeita a revisão humana.

## Como funciona

```text
Transcrição anonimizada
        ↓
Limpeza e deduplicação
        ↓
Chunking com tokenizer BERTimbau
        ↓
Classificação de oportunidade por chunk
        ↓
Agregação e detecção de contexto misto por reunião
        ↓
Busca semântica na base TOTVS com multilingual-e5-small
        ↓
Insight estruturado + produto + evidência + fontes
```

## Modelos e estratégias avaliados

Para a classificação de oportunidade foram comparados:

- TF-IDF + Regressão Logística;
- BERTimbau com fine-tuning.

O BERTimbau foi selecionado como modelo provisório por apresentar melhor
desempenho equilibrado na pseudo-validação. O baseline lexical continua sendo
uma referência barata e obteve o maior recall nesse experimento.

Para a recuperação da base foram comparados:

- busca lexical BM25 com aliases;
- embeddings do BERTimbau base;
- recuperação híbrida;
- `multilingual-e5-small`, especializado em busca semântica.

O E5 foi o melhor retriever no conjunto inicial de 32 consultas, com Recall@5
de 98,44%, Hit@5 de 100%, MRR de 92,19% e nDCG@5 de 93,47%.

Essas métricas são experimentais. O conjunto de consultas foi construído a
partir da própria base, e o classificador ainda foi treinado com pseudo-rótulos.
Os números não representam precisão comprovada em produção.

## Estado atual

O pipeline completo já processa:

- 1.174 registros de entrada;
- 1.126 reuniões únicas após remover 48 duplicatas;
- 29.972 chunks;
- 107 documentos na base de conhecimento TOTVS;
- 29 grupos de aliases de produtos, módulos e concorrentes.

A integração final gera
`data/processed/meeting_commercial_insights.jsonl`, contendo apenas IDs,
probabilidades, documentos recuperados, produtos, categorias, políticas de
grounding e fontes.

A aplicação completa marcou muitas reuniões como candidatas e encontrou grande
quantidade de contexto misto. Isso indica que os limiares e a agregação precisam
ser calibrados com reuniões rotuladas por pessoas antes de qualquer uso real.

## Estrutura do projeto

```text
Wedjat/
├── data/
│   ├── raw/                 # transcrições anonimizadas
│   ├── knowledge_base/      # base TOTVS, aliases e consultas de avaliação
│   └── processed/           # reuniões versionadas e demais artefatos locais
├── notebooks/               # Colab (00) e módulos numerados de 01 a 18
├── reports/
│   ├── figures/             # gráficos e matrizes de confusão
│   └── metrics/             # métricas agregadas dos experimentos
├── COLAB_README.md           # instruções específicas para Google Colab
├── O_QUE_FIZEMOS_NO_PROJETO.md
├── TODO.md
└── requirements.txt
```

O histórico técnico detalhado, com todas as decisões e resultados por notebook,
está em [O_QUE_FIZEMOS_NO_PROJETO.md](O_QUE_FIZEMOS_NO_PROJETO.md).

## Como executar

### Google Colab

Para executar tudo em uma única aba, use
`notebooks/00_projeto_completo_colab.ipynb`. Ele reúne as 11 etapas, preserva
as explicações e libera a memória da GPU entre os modelos.

O pacote `Wedjat_Entrega_Colab_Notebook_Unico.zip` contém somente esse notebook,
os dados e os arquivos auxiliares necessários. Siga as instruções de
[COLAB_README.md](COLAB_README.md) e ative um runtime com GPU.

### Ambiente local

Recomenda-se Python 3.12 e uma GPU CUDA para os notebooks do BERTimbau.

```bash
python -m venv .venv
```

Ative o ambiente virtual, instale uma versão do PyTorch apropriada para sua GPU
e depois execute:

```bash
pip install -r requirements.txt
jupyter notebook
```

O PyTorch não é fixado no `requirements.txt`, porque a distribuição correta
depende da versão de CUDA ou do runtime do Colab.

Para reproduzir a preparação dos dados, execute o notebook 01 com o NDJSON
versionado em `data/raw/ANON_transcricao.json`. O arquivo de entrada e
`data/processed/meetings.jsonl` fazem parte do repositório. A base contém
1.126 reuniões únicas e reproduz os agregados já descritos neste projeto.
Sem prova de independência, seu uso serve para testar o funcionamento, não
como validação em reuniões inéditas.

Para a Sprint 4, abra `notebooks/18_analise_comercial.ipynb`. Ele
carrega os notebooks 12 a 17 no mesmo kernel. A execução está separada em
células para configurar, carregar, analisar, revisar labels e JSON, e salvar
somente quando houver um caminho de saída. Cada funcionalidade permanece em
um notebook menor, explicado e testado separadamente.

O guia [docs/sprint4_notebooks.md](docs/sprint4_notebooks.md) descreve os modos
de análise, os três formatos de entrada, os modelos opcionais, cache offline,
persistência do JSON e exemplos de configuração.

## Principais artefatos

- `reports/metrics/model_comparison.json`: comparação dos classificadores;
- `reports/metrics/rag_retrieval_evaluation.json`: avaliação inicial do RAG;
- `reports/metrics/sentence_embeddings_retrieval.json`: avaliação do E5;
- `reports/metrics/final_integration_summary.json`: resumo do pipeline completo;
- `data/processed/meeting_commercial_insights.jsonl`: resultado por reunião.

## Privacidade e uso responsável

As transcrições anonimizadas de entrada e `meetings.jsonl` são versionadas
neste projeto estudantil. Outros artefatos gerados, inclusive checkpoints e
índices, continuam fora do Git. Mantenha o acesso ao runtime e ao Drive conforme
as regras do projeto.

O Wedjat deve ser usado como apoio à revisão comercial. Ele não deve tomar
decisões automáticas sobre clientes, vendedores ou oportunidades enquanto não
houver avaliação humana representativa, calibração e monitoramento.

## Próximas funcionalidades

As próximas evoluções planejadas são:

1. concluir a anotação humana da fila reservada;
2. criar um conjunto de teste final exclusivamente humano;
3. medir precisão real dos pseudo-rotuladores e classificadores;
4. calibrar limiares e agregação no nível da reunião;
5. implementar NER para extrair produtos, empresas, dores e concorrentes;
6. usar entidades extraídas como filtros da recuperação semântica;
7. separar fatos e inferências dentro de documentos mistos da base;
8. registrar data de verificação e validade das fontes;
9. avaliar o pipeline ponta a ponta com reuniões anotadas;
10. aprimorar as células de consulta e revisão humana nos notebooks;
11. gerar respostas narrativas com citações verificáveis;
12. adicionar monitoramento de qualidade, drift e feedback humano.

O acompanhamento detalhado das tarefas está em [TODO.md](TODO.md).

---

## 👥 Integrantes
- Beatriz Cortez - RM561431
 
- Bruno Alves - RM563986
 
- Gabriel Augusto - RM564126
 
- Davi Duarte - RM566316
 
- Raphaela Tatto - RM572059
