# Wedjat

O Wedjat transforma transcrições extensas de reuniões em dados preparados para
experimentos de classificação e extração de insights de negócio.

## Fluxo em notebooks

O desenvolvimento é centralizado em notebooks executáveis e documentados.

### 01 — Limpeza e entendimento das reuniões

`notebooks/01_preparacao_dados.ipynb` contém o código completo que:

1. lê o arquivo NDJSON em streaming, sem carregar todas as transcrições na memória;
2. valida `ID_MEETING` e `ANON_TRANSCRICAO`;
3. normaliza apenas espaços e quebras de linha, sem remover palavras;
4. remove duplicatas exatas pelo identificador da reunião;
5. interrompe o processamento se um mesmo ID possuir conteúdos diferentes;
6. acrescenta contagens de caracteres e turnos de locutor;
7. gera um resumo sem copiar transcrições para logs ou relatórios;
8. apresenta o esquema e estatísticas agregadas para orientar o chunking.

Saídas:

- `data/processed/meetings.jsonl`: uma reunião única por linha;
- `reports/metrics/data_preparation_summary.json`: auditoria numérica do processo.

### 02 — Base de conhecimento TOTVS

`notebooks/02_base_conhecimento_rag.ipynb` carrega e valida a base já convertida
em `data/knowledge_base/totvs_rag_kb_v1.json`, audita sua estrutura e executa
uma busca lexical mínima que servirá como baseline para o RAG.

### 03 — Tokenização e chunking

`notebooks/03_tokenizacao_e_chunks.ipynb` usa o tokenizer do
`neuralmind/bert-base-portuguese-cased` para criar janelas de até 510 tokens de
conteúdo, com sobreposição-alvo de 64 tokens e limites em palavras completas.
Cada chunk preserva reunião, ordem, offsets de caracteres e locutores.

Saídas:

- `data/processed/chunks_bertimbau.jsonl`: chunks com texto, ignorados pelo Git;
- `reports/metrics/chunking_summary.json`: auditoria agregada do chunking.

### 04 — Alvo supervisionado e BERTimbau

`notebooks/04_alvo_e_bertimbau.ipynb` define oportunidade comercial como
primeiro alvo binário, documenta o guia inicial de anotação e demonstra com
textos sintéticos como o BERTimbau tokeniza e representará os chunks. O
notebook também comprova que os dados atuais ainda não possuem rótulos.

### 05 — Supervisão fraca e split seguro

`notebooks/05_supervisao_fraca_e_divisao.ipynb` combina um rotulador por regras
apoiado pelo RAG com um rotulador semântico por protótipos do BERTimbau. Somente
as concordâncias são salvas como pseudo-rótulos; previsões automáticas não são
tratadas como verdade-terreno.

Na primeira execução foram analisados 3.000 chunks das 1.126 reuniões e gerados
906 pseudo-rótulos: 376 de oportunidade e 530 de não oportunidade. A divisão de
desenvolvimento usa 679 desses pseudo-rótulos, com 388 reuniões no treino e 98
na validação. Uma fila cega com 150 chunks de 150 reuniões reservadas foi criada
para auditoria humana. Não existe vazamento entre treino, validação e auditoria.

Saídas:

- `data/processed/pseudo_labels_opportunity.jsonl`: dados de desenvolvimento;
- `data/processed/annotation_queue_opportunity.jsonl`: fila para rótulos humanos;
- `reports/metrics/weak_supervision_summary.json`: resultados agregados.

### 06 — Baseline TF-IDF + Regressão Logística

`notebooks/06_baseline_oportunidade.ipynb` treina o baseline no split agrupado
do notebook 05. O modelo usa unigramas e bigramas, `class_weight=balanced` e
limiar 0,5. O vocabulário é ajustado somente nos 539 chunks de treino e avaliado
em 140 chunks de 98 reuniões exclusivas.

Contra os pseudo-rótulos, o baseline obteve accuracy de 95,71%, precision de
90,63%, recall de 100% e F1 de 95,08% para oportunidade. A matriz de confusão
foi `[[76, 6], [0, 58]]`. Esses valores provavelmente são otimistas porque parte
dos pseudo-rótulos também foi criada com sinais lexicais; eles não substituem a
avaliação humana.

Saídas:

- `reports/metrics/baseline_tfidf_logreg_metrics.json`: métricas completas;
- `reports/figures/baseline_tfidf_logreg_confusion_matrix.png`: matriz;
- `data/processed/baseline_tfidf_logreg_validation_predictions.jsonl`: previsões;
- `data/processed/baseline_tfidf_logreg_errors.jsonl`: erros sem transcrições;
- `data/processed/baseline_tfidf_logreg.joblib`: modelo local não versionado.

### 07 — Fine-tuning do BERTimbau

`notebooks/07_treinamento_bertimbau.ipynb` ajusta o checkpoint
`neuralmind/bert-base-portuguese-cased` no mesmo split do baseline. O treino usa
512 tokens, batch físico 4, acumulação de gradiente 2, FP16, pesos de classe,
AdamW e três épocas. Assim, cada entrada preserva o limite completo definido no
chunking.

O melhor checkpoint foi o da terceira época. Contra os pseudo-rótulos, obteve
accuracy de 97,86%, precision de 96,61%, recall de 98,28% e F1 de 97,44% para
oportunidade. A matriz foi `[[80, 2], [1, 57]]`. Na RTX 3050, o treinamento
levou aproximadamente 104 segundos e atingiu pico de 2,14 GB de VRAM.

Saídas:

- `reports/metrics/bertimbau_finetuning_metrics.json`: configuração e métricas;
- `reports/figures/bertimbau_confusion_matrix.png`: matriz de confusão;
- `data/processed/bertimbau_opportunity_best/`: melhor checkpoint local;
- `data/processed/bertimbau_validation_predictions.jsonl`: previsões;
- `data/processed/bertimbau_validation_errors.jsonl`: erros sem transcrições.

Esses resultados permitem a comparação técnica com o baseline, mas continuam
sujeitos ao viés dos pseudo-rótulos e não substituem o conjunto humano final.

### 08 — Comparação dos modelos

`notebooks/08_comparacao_modelos.ipynb` valida que os dois modelos foram avaliados
nos mesmos 140 chunks de 98 reuniões e recalcula todas as métricas de forma
pareada. Também executa teste exato de McNemar e bootstrap com duas mil
reamostragens agrupadas por reunião.

O BERTimbau venceu em accuracy, precision, F1 de oportunidade e F1 macro. O
baseline venceu na métrica principal, recall de oportunidade, por 100% contra
98,28%. Os modelos acertaram juntos 133 chunks; o baseline acertou sozinho um,
o BERTimbau acertou sozinho quatro e ambos erraram dois.

O teste de McNemar resultou em `p=0,375`, e os intervalos de 95% do bootstrap
incluem zero para as diferenças de accuracy e F1. Assim, a vantagem observada do
BERTimbau não é conclusiva nesta amostra.

Mesmo com essa incerteza, o **BERTimbau foi selecionado como melhor modelo
provisório do experimento atual**: venceu quatro das cinco métricas, reduziu o
total de erros de seis para três e obteve Brier score 0,0159 contra 0,1061 do
baseline. O baseline continua sendo a opção mais barata e venceu no recall.

Com custo unitário para revisar um falso positivo, o ponto de equilíbrio ocorre
quando um falso negativo custa quatro revisões: abaixo disso o BERTimbau tem menor
custo observado; acima disso o baseline tem menor custo. O BERTimbau ocupa cerca
de 415,54 MB contra 0,69 MB do baseline e exige muito mais treinamento. A seleção
para produção permanece pendente até a avaliação humana.

Saídas:

- `reports/metrics/model_comparison.json`: comparação e decisão provisória;
- `reports/figures/model_comparison_metrics.png`: métricas lado a lado;
- `reports/figures/model_comparison_confusion_matrices.png`: matrizes pareadas;
- `data/processed/model_comparison_disagreements.jsonl`: divergências sem texto.

### 09 — Evolução e avaliação do retrieval do RAG

`notebooks/09_evolucao_busca_rag.ipynb` compara quatro retrievers sobre 32
consultas curadas: BM25 com aliases, embeddings do BERTimbau base, fusão híbrida
por RRF e híbrida com reranking por evidência. A avaliação calcula Recall@1/3/5,
Hit@1/3/5, MRR e nDCG.

O melhor método foi BM25 com aliases, com Recall@5 de 93,75%, Hit@5 de 96,88%,
MRR de 76,64% e nDCG@5 de 80,36%. Mean pooling do BERTimbau base obteve
Recall@5 de 67,19%, mostrando que o encoder genérico não é automaticamente um
bom modelo de similaridade. A fusão híbrida alcançou Recall@5 de 85,94%; o bônus
por evidência não melhorou o resultado e não foi escolhido como padrão.

O notebook também audita keywords, aplica 29 grupos de aliases e cria um contrato
de contexto que transporta URLs, nível de evidência e política de uso. Hipóteses
devem permanecer hipóteses, e documentos sem fonte não podem sustentar fatos.

Saídas:

- `data/knowledge_base/rag_aliases.json`: aliases versionáveis;
- `data/knowledge_base/rag_evaluation_queries.json`: conjunto de avaliação;
- `reports/metrics/rag_retrieval_evaluation.json`: métricas e rankings;
- `reports/metrics/rag_keyword_audit.json`: auditoria das keywords;
- `reports/figures/rag_retrieval_comparison.png`: comparação visual;
- `data/processed/rag_bertimbau_embeddings.npz`: embeddings locais.

### 10 — Embeddings especializados

`notebooks/10_busca_embeddings_e5.ipynb` avalia o encoder
`intfloat/multilingual-e5-small` com prefixos `query:` e `passage:`, mean pooling
com máscara e normalização L2. Ele é comparado de forma pareada ao BM25, ao
BERTimbau base e à fusão BM25 + E5.

O E5 foi o vencedor: Recall@5 98,44%, Hit@5 100%, MRR 92,19% e nDCG@5
93,47%. O índice tem 384 dimensões e foi gerado na RTX 3050. A fusão com BM25
empatou em Recall@5, mas teve MRR menor; por isso o E5 isolado passou a ser o
retriever padrão provisório.

Saídas:

- `reports/metrics/sentence_embeddings_retrieval.json`: métricas e rankings;
- `reports/figures/sentence_embeddings_retrieval.png`: gráfico comparativo;
- `data/processed/rag_multilingual_e5_small_embeddings.npz`: índice local.

### 11 — Integração final

`notebooks/11_integracao_reunioes.ipynb` executa o classificador BERTimbau nos
29.972 chunks, agrega os resultados nas 1.126 reuniões e consulta a base TOTVS
com o E5 vencedor. O resultado por reunião contém probabilidades, índices dos
chunks de apoio, produtos/categorias, nível de evidência, política de uso e URLs,
mas nunca salva o texto das transcrições.

A regra operacional provisória exige pelo menos dois chunks com probabilidade
de oportunidade ≥ 0,80 e densidade mínima de 5% na reunião. Foram geradas 975
reuniões candidatas, todas com ao menos uma evidência com fonte. Porém 935 também
possuem chunks fortemente negativos, indicando contexto misto. Essa taxa alta é
um alerta de calibração: os pseudo-rótulos não permitem estimar precisão real nem
selecionar o pipeline para produção sem uma avaliação humana no nível da reunião.

Saídas:

- `data/processed/meeting_commercial_insights.jsonl`: insights por reunião sem texto;
- `reports/metrics/final_integration_summary.json`: cobertura, contratos e limitações.

## GPU local e Google Colab

Os notebooks detectam automaticamente CUDA e usam CPU como fallback. O notebook
05 foi validado em uma NVIDIA GeForce RTX 3050 de 8 GB com batch 8 e sequências
de até 512 tokens. No Colab, selecione um ambiente com GPU, abra a raiz do
projeto e instale as dependências com `pip install -r requirements.txt`.

O PyTorch não fica fixado no arquivo de dependências, pois a distribuição correta
depende do CUDA local e o Colab já fornece uma versão compatível com seu runtime.

No VS Code, selecione `Wedjat (Python 3.12 CUDA)`. Esse kernel aponta diretamente
para o Python que contém NumPy, scikit-learn, Transformers e PyTorch com CUDA.
Não use `Python 3.12 (FIAP)`, pois ele pertence a outro projeto.

Cada notebook possui células Markdown que registram as decisões metodológicas
antes das células de código correspondentes.

