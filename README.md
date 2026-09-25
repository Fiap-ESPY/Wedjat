<p align="center">
  <img src="assets/wedjat-logo.png" alt="Logo Wedjat" width="650">
</p>

**Inteligência comercial que enxerga além do óbvio.**

O Wedjat é um projeto estudantil de inteligência comercial para a TOTVS. O protótipo recebe **uma nova transcrição** e devolve indicadores estruturados para revisão da área comercial: produto candidato, sentimento, risco de churn, oportunidade, termos principais e recomendação de ação. A marca acima e a arte ao final vêm da apresentação do Challenge e preservam a identidade visual em azul petróleo, branco e laranja.

> O pitch apresenta uma visão mais ampla, com captura de áudio, Wedjat Touch, interfaces por perfil e briefing 360°. Esses recursos são conceitos da apresentação; o protótipo deste repositório começa com uma transcrição já disponível e produz uma análise em notebooks.

## Fluxo do protótipo

```text
Transcrição → Processamento → Modelos ou fallback → Indicadores → Recomendação
```

O ponto de entrada é [`notebooks/19_analise_final.ipynb`](notebooks/19_analise_final.ipynb). Por padrão, ele analisa dez transcrições distintas, chamando `analisar_transcricao(transcricao, modo="full")` do [notebook 18](notebooks/18_analise_comercial.ipynb) uma vez para cada transcrição. A saída JSON preserva cada texto de entrada e informa, por indicador, label, score, tipo de score, mecanismo utilizado e fontes quando há produto candidato. O notebook final grava o JSON completo e mostra seus dados em tabelas pandas; **toda ação exige revisão humana**.

| Saída | O que representa |
| --- | --- |
| Produto principal e candidatos | Ranking de documentos da base TOTVS, com fontes e correspondência explícita quando encontrada. |
| Sentimento | Sinal de linguagem positiva, neutra, negativa ou mista. |
| Risco de churn | Sinal comercial baixo, médio ou alto; não é previsão calibrada de cancelamento. |
| Oportunidade comercial | Sinal de necessidade detectada ou não detectada. |
| Termos principais | Até dez termos relevantes para a análise. |
| Recomendação de ação | Próximo passo sugerido, com critérios, motivo e revisão humana obrigatória. |

Os scores `model_probability`, `normalized_cosine_similarity` e `heuristic` têm significados diferentes. A legenda `score_legend` acompanha cada resultado; nenhum desses valores deve ser lido automaticamente como probabilidade de compra.

## Executar as análises

Instale as dependências de `requirements.txt` em um ambiente Python 3.12. Para usar modelos, instale antes a variante do PyTorch adequada ao seu sistema e à sua GPU pelo [seletor oficial](https://pytorch.org/get-started/locally/). O PyTorch não é fixado no arquivo de requisitos porque a distribuição depende do hardware.

```bash
python -m venv .venv
# Ative .venv no seu sistema operacional.
python -m pip install -r requirements.txt
python -m pip check
jupyter notebook
```

Abra o notebook 19 no kernel `Wedjat (Python 3.12 CUDA)` e execute **Run All / Executar tudo**. A configuração inicial analisa dez registros anonimizados com IDs de reunião distintos do arquivo NDJSON do projeto:

```python
ORIGEM = "arquivo"
ARQUIVO_ENTRADA = "data/raw/ANON_transcricao.json"
INDICES_REGISTROS = [117, 137, 141, 213, 254, 369, 394, 401, 418, 525]
ARQUIVO_SAIDA = "data/processed/analises_finais_10.json"
```

O arquivo contém 1.174 registros; a lista de índices pode ser alterada para analisar outras reuniões. Os dez exemplos padrão foram escolhidos entre textos de 1.500 a 3.500 caracteres para uma execução local verificável; não formam uma amostra aleatória. Para uma entrada própria, use `ORIGEM="texto"` e cole o conteúdo em `TRANSCRICAO_DIRETA`, ou informe outro `.txt`, objeto `.json` ou `.jsonl` em `ARQUIVO_ENTRADA`. O notebook 19 exige CUDA e todos os modelos em `full`. Ele salva um JSON com uma análise por transcrição, lê o arquivo salvo e exibe tabelas pandas de indicadores, produtos candidatos e campos do JSON. O arquivo completo fica em `data/processed/`, ignorado pelo Git por conter textos e IDs.

| Modo | Comportamento |
| --- | --- |
| `fallback` | Usa busca BM25 com aliases e regras lexicais, sem carregar modelos pesados. |
| `auto` | Tenta os modelos disponíveis e registra os motivos de fallback por componente. |
| `full` | Exige os modelos e os artefatos locais; interrompe com erro claro quando faltam. Foi reproduzido na RTX 3050. |

| Indicador | Modelo do caminho `full` | Fallback |
| --- | --- | --- |
| Produto | `intfloat/multilingual-e5-small` e índice do notebook 10 | BM25 com aliases |
| Sentimento | `pysentimiento/bertweet-pt-sentiment` | Regras lexicais |
| Risco de churn | `MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli` | Regras lexicais |
| Oportunidade | Checkpoint BERTimbau do notebook 07 | Regras comerciais |

Os modelos de sentimento e churn não foram treinados para prever resultados comerciais nestas reuniões. O score de churn é um sinal de triagem, não uma probabilidade calibrada de cancelamento.

### Executar com modelos no PC com GPU

A partir da raiz do projeto, instale o PyTorch adequado à GPU, execute `python -m pip install -r requirements.txt` e confira `python -c "import torch; print(torch.cuda.is_available())"`. No Jupyter, execute integralmente, nesta ordem:

1. `03_tokenizacao_e_chunks.ipynb` — gera `data/processed/chunks_bertimbau.jsonl`.
2. `05_supervisao_fraca_e_divisao.ipynb` — gera pseudo-rótulos e a fila reservada de auditoria.
3. `07_treinamento_bertimbau.ipynb` — gera `data/processed/bertimbau_opportunity_best/`.
4. `10_busca_embeddings_e5.ipynb` — gera `data/processed/rag_multilingual_e5_small_embeddings.npz`.

Esses notebooks estão na pasta `notebooks/`. BERTimbau e E5 são baixados quando não estão no cache; o modo `full` também carrega os modelos de sentimento e de NLI para churn. Confira a existência do checkpoint e do índice antes de executar o notebook 19. Registre data, versões, GPU, mecanismos e tempo sem copiar transcrições ou IDs para um relatório público. Preserve os relatórios versionados se quiser comparar métricas: os notebooks de treino podem reescrevê-los localmente.

Em 25/09/2026, os **19 notebooks anteriores passaram** no kernel `wedjat` com PyTorch CUDA 13.0 e RTX 3050. O notebook 18 executou em `full` com E5, Pysentimiento, MiniLM e BERTimbau carregados em CUDA: 25,64 s para uma transcrição sintética, pico de 1.798 MiB de VRAM, três produtos candidatos com fontes e revisão humana obrigatória. O [resumo da execução](reports/metrics/notebook_gpu_run.json) contém apenas resultados agregados. O notebook 19 passou em `full` com dez transcrições reais distintas, gravou o JSON completo e exibiu as três tabelas pandas.

Para reproduzir todas as etapas anteriores em uma única aba do **Google Colab**, use `notebooks/00_projeto_completo_colab.ipynb` com runtime de GPU, os dados deste repositório e `pip install -r requirements.txt`. O notebook único reúne as etapas 01 a 11; o notebook 18 é a demonstração interativa da Sprint 4.

## Resultados e limites

A preparação registra 1.174 entradas NDJSON e 1.126 reuniões únicas após 48 duplicatas exatas. O histórico experimental registra 29.972 chunks, 107 documentos na base TOTVS e 29 grupos de aliases. A base recebida tem agregados iguais aos da base histórica; sem hashes ou IDs antigos comparáveis, **não há prova de que seja um teste independente**.

BERTimbau foi escolhido para o caminho com modelos **do protótipo** na classificação de oportunidade. Em 140 chunks avaliados contra pseudo-rótulos, obteve F1 de oportunidade 0,974 e 3 erros; TF-IDF + Regressão Logística obteve F1 de 0,951, 6 erros e recall maior (1,000 contra 0,983). A diferença de acertos não foi conclusiva (McNemar p = 0,375), e o baseline é muito menor e mais barato. O Brier score foi 0,016 para BERTimbau e 0,106 para o baseline; no custo experimental registrado, o baseline passa a ser preferível se um falso negativo custar mais que quatro revisões de falso positivo. A escolha para produção depende de dados humanos e custos reais. Números completos: [`model_comparison.json`](reports/metrics/model_comparison.json).

Na busca, `multilingual-e5-small` obteve Recall@5 de 0,984 e MRR de 0,922 em 32 consultas curadas da própria base, contra 0,938 e 0,766 de BM25 com aliases. O E5 é o retriever do caminho com modelos; BM25 é o fallback. Um documento comparativo pode aparecer acima do produto mencionado, por isso o produto principal e suas fontes exigem conferência humana. Números completos: [`sentence_embeddings_retrieval.json`](reports/metrics/sentence_embeddings_retrieval.json).

O protótipo passou por **35 testes determinísticos**, pelos 19 notebooks anteriores e pelo notebook 19 em `full` com dez transcrições do projeto. O notebook 18 também passou de ponta a ponta em `fallback` e `full`. Um smoke test adicional processou 20 reuniões da base histórica em `fallback`, sem falhas de contrato. Esses testes verificam funcionamento; **não medem a qualidade das labels nem a generalização**. Consulte [`sprint4_existing_data_smoke.json`](reports/metrics/sprint4_existing_data_smoke.json), o [resumo da GPU](reports/metrics/notebook_gpu_run.json) e o plano em [`TODO.md`](TODO.md).

### Dez análises de transcrições do projeto

Na execução de 25/09/2026, o notebook 19 processou **10 transcrições de reuniões distintas** em `full` na RTX 3050. As dez preservaram o texto original, usaram modelos nos quatro componentes, trouxeram candidatos com fontes e exigiram revisão humana. O JSON integral está em `data/processed/analises_finais_10.json` (arquivo local ignorado pelo Git). O [resumo agregado em JSON](reports/metrics/analise_final_10_resumo.json) não contém transcrições nem IDs.

| Indicador | Contagens nas 10 transcrições |
| --- | --- |
| Sentimento | 10 `neutro` |
| Risco de churn | 9 `medio`, 1 `alto` |
| Oportunidade comercial | 1 `detectada`, 9 `nao_detectada` |
| Recomendação de ação | 9 `revisar_manualmente`, 1 `acionar_retencao` |
| Produto principal candidato | 4 TOTVS Backoffice – Linha RM; 3 RD Station Conversas; 1 RD Station Mentor IA; 1 TOTVS Distribuição e Varejo – Linha WinThor; 1 TOTVS CRM Gestão de Clientes |

A execução com modelos em cache e modo offline levou 27,24 s no total e atingiu 1.882,5 MiB de memória de GPU. A checagem encontrou 30 produtos candidatos com fontes, todos provenientes de documentos `document_type="produto"`. Essa restrição foi aplicada após a primeira execução ter retornado indevidamente “Taxonomia de entidades” como produto principal nas dez transcrições. **Essas contagens são saídas exploratórias do modelo, não métricas de acerto**: a amostra foi escolhida por tamanho, pertence à base histórica e não possui rótulos humanos para confronto.

### Revisão exploratória dos 150 chunks

Os 150 chunks da fila reservada foram lidos e receberam rótulos de IA em `data/processed/ai_labels_opportunity.jsonl`: 61 `oportunidade`, 61 `nao_oportunidade` e 28 `revisao` por contexto insuficiente ou ambíguo. Cada registro traz o identificador do chunk, rótulo, confiança e justificativa curta; nenhum campo `human_label` foi preenchido. A fila e os rótulos por chunk são artefatos locais ignorados pelo Git, conforme a política de dados do repositório. Apenas as [contagens agregadas](reports/metrics/ai_label_review_summary.json) são versionadas.

Esses rótulos são uma segunda leitura por IA, **não um gabarito humano independente**. Como não há rótulos humanos disponíveis, continuam pendentes a medição de precisão real, a calibração de limiares e a avaliação em transcrições inéditas com independência comprovada da base histórica. A seleção de modelos para produção permanece em aberto.

## Organização

```text
assets/           logo e arte final extraídos do pitch
notebooks/        notebook único Colab (00), etapas 01–11, análise 12–18 e entrada final 19
data/raw/         transcrições anonimizadas versionadas
data/processed/   reuniões versionadas; checkpoints e índices locais ignorados
data/knowledge_base/  documentos, aliases e consultas de avaliação
reports/metrics/ métricas agregadas dos experimentos
tests/           testes determinísticos do contrato e das recomendações
```

As transcrições anonimizadas e `data/processed/meetings.jsonl` fazem parte deste projeto estudantil. Checkpoints, índices e outros artefatos gerados ficam fora do Git. A solução apoia a revisão comercial; nenhuma sugestão deve acionar clientes automaticamente antes de avaliação humana representativa e calibração.

## Skills de engenharia

As 25 skills de [`mattpocock/skills`](https://github.com/mattpocock/skills) estão em `.agents/skills/`, com a licença MIT original. Use [`$wedjat-matt-orchestrator`](.agents/skills/wedjat-matt-orchestrator/SKILL.md) para escolher um fluxo de investigação, planejamento, implementação ou revisão neste projeto. O orquestrador mantém backlog, critérios e bloqueios em `TODO.md` e segue o vocabulário de `CONTEXT.md`.

## Equipe

- Beatriz Cortez — RM561431
- Bruno Alves — RM563986
- Gabriel Augusto — RM564126
- Davi Duarte — RM566316
- Raphaela Tatto — RM572059

## Conheça o Wedjat

<p align="center">
  <img src="assets/wedjat-identidade.png" alt="Arte final Wedjat com QR code para conhecer a plataforma" width="100%">
</p>
