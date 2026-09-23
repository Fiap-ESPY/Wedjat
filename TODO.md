# TODO — Projeto Wedjat

Este arquivo acompanha o que já foi concluído, o que está em andamento e os
próximos passos do projeto. Atualize os checkboxes a cada avanço relevante.

## Legenda

- `[x]` concluído
- `[ ]` pendente
- `[~]` em andamento
- `[!]` bloqueado ou depende de decisão

## Concluído

- [x] Organizar a estrutura inicial do repositório.
- [x] Adicionar as transcrições anonimizadas em `data/raw/`.
- [x] Confirmar que a entrada é NDJSON com 1.174 registros.
- [x] Implementar a limpeza conservadora das transcrições no notebook.
- [x] Validar `ID_MEETING` e `ANON_TRANSCRICAO`.
- [x] Normalizar espaços e quebras de linha sem remover palavras ou stopwords.
- [x] Remover 48 duplicatas exatas.
- [x] Gerar 1.126 reuniões únicas em `data/processed/meetings.jsonl`.
- [x] Gerar o relatório agregado de preparação dos dados.
- [x] Manter transcrições brutas e processadas fora do Git.
- [x] Analisar a base de conhecimento comercial TOTVS.
- [x] Converter a base do RAG para JSON.
- [x] Validar 107 chunks, 107 IDs únicos e 52 URLs de fontes.
- [x] Criar `notebooks/01_data_understanding.ipynb` com explicações e código.
- [x] Criar `notebooks/02_rag_knowledge_base.ipynb` com auditoria e busca lexical.
- [x] Executar integralmente os notebooks 01 e 02.
- [x] Atualizar o `README.md` para o fluxo notebook-first.

## Próximo passo

- [x] Criar `notebooks/03_tokenization_and_chunking.ipynb`.
- [x] Separar cada transcrição em turnos de locutor.
- [x] Confirmar se todas as reuniões seguem o padrão `[LOCUTOR N]:`.
  Resultado: 48 não possuem marcador e 100 têm texto antes do primeiro marcador.
- [x] Escolher o tokenizer/checkpoint do BERTimbau:
  `neuralmind/bert-base-portuguese-cased`.
- [x] Medir a distribuição do número de tokens por reunião e por turno.
- [x] Definir `max_tokens=510` e `overlap_tokens=64`.
- [x] Criar chunks baseados em tokens, sem cortar palavras arbitrariamente.
- [x] Preservar `meeting_id`, ordem, locutor e janela de contexto em cada chunk.
- [x] Criar validações para garantir que nenhum conteúdo seja perdido ou duplicado
  indevidamente pelo chunking.
- [x] Gerar 29.972 chunks em `data/processed/chunks_bertimbau.jsonl`.
- [x] Confirmar que nenhum chunk ultrapassa 510 tokens de conteúdo.

## Definição do problema supervisionado

- [x] Confirmar o objetivo e os requisitos oficiais da Sprint 3.
- [x] Selecionar inicialmente `oportunidade` versus `nao_oportunidade`.
- [x] Definir exatamente as classes e seus critérios.
- [x] Definir o chunk como unidade rotulada e a reunião como unidade de split.
- [x] Criar um guia inicial para exemplos positivos, negativos e ambíguos.
- [x] Verificar se já existem rótulos confiáveis nos dados.
  Resultado: não existe campo de rótulo; será necessária anotação humana.
- [x] Criar `notebooks/04_target_and_bertimbau.ipynb`.
- [x] Definir uma fila inicial cega com 150 chunks para auditoria humana.
- [x] Medir a distribuição inicial dos pseudo-rótulos.
  Resultado: 376 oportunidades e 530 não oportunidades em 906 concordâncias.
- [ ] Medir a distribuição dos rótulos humanos após a auditoria.
- [x] Separar rótulos humanos, pseudo-rótulos e sinais individuais dos rotuladores.

## Supervisão fraca inicial

- [x] Criar `notebooks/05_weak_supervision_and_split.ipynb`.
- [x] Criar um rotulador por regras apoiado pelo vocabulário comercial do RAG.
- [x] Criar um rotulador semântico por protótipos com BERTimbau.
- [x] Aceitar como pseudo-rótulo somente a concordância dos dois rotuladores.
- [x] Processar uma amostra reproduzível de 3.000 chunks das 1.126 reuniões.
- [x] Gerar 906 pseudo-rótulos, com cobertura de 30,2% da amostra.
- [x] Gerar `data/processed/pseudo_labels_opportunity.jsonl`.
- [x] Gerar `data/processed/annotation_queue_opportunity.jsonl` com 150 itens.
- [x] Registrar apenas resultados agregados em
  `reports/metrics/weak_supervision_summary.json`.
- [ ] Preencher a fila de auditoria com rótulos humanos.
- [ ] Calcular a precisão real de cada rotulador contra os rótulos humanos.

## Divisão dos dados

- [x] Criar divisão de desenvolvimento `train/validation` dos pseudo-rótulos,
  agrupada por `ID_MEETING`.
- [ ] Criar o conjunto de teste final exclusivamente com rótulos humanos.
- [x] Garantir que chunks da mesma reunião nunca apareçam em partições diferentes.
- [x] Aplicar estratificação por classe no nível da reunião.
- [x] Fixar e documentar a semente aleatória (`42`).
- [x] Criar uma validação automática contra vazamento entre partições.
  Resultado: zero reuniões compartilhadas entre treino, validação e auditoria;
  ficaram 679 pseudo-rótulos de desenvolvimento em 486 reuniões.

## Modelo baseline — Sprint 3

- [x] Criar a etapa de anotação inicial e split no notebook 05.
- [x] Criar uma fila reproduzível para anotação humana.
- [x] Criar `notebooks/06_baseline_tfidf_logreg.ipynb`.
- [x] Implementar TF-IDF + Regressão Logística.
- [x] Treinar usando a divisão agrupada por reunião.
- [x] Calcular matriz de confusão.
  Resultado nos pseudo-rótulos: `[[76, 6], [0, 58]]`.
- [x] Calcular precisão, recall, F1 e acurácia.
  Resultado para oportunidade: precision 90,63%, recall 100% e F1 95,08%;
  accuracy geral 95,71%.
- [x] Registrar métricas por classe, macro e weighted.
- [x] Analisar os principais erros do baseline sem expor dados sensíveis.
  Resultado: seis falsos positivos e nenhum falso negativo contra os
  pseudo-rótulos; o manifesto contém apenas IDs, classes e probabilidades.

## BERTimbau — Sprint 3

- [x] Criar `notebooks/07_bertimbau_finetuning.ipynb`.
- [x] Registrar checkpoint, tokenizer e versão atual do Transformers.
- [x] Preparar datasets e DataLoaders no formato esperado pelo BERTimbau.
- [x] Fazer fine-tuning do BERTimbau para o mesmo alvo do baseline.
- [x] Avaliar na mesma validação agrupada usada pelo baseline.
  Resultado: 539 chunks no treino e 140 na validação, com zero vazamento.
- [ ] Avaliar os dois modelos no conjunto de teste humano final.
- [x] Calcular matriz de confusão, precisão, recall, F1 e acurácia.
  Resultado nos pseudo-rótulos: matriz `[[80, 2], [1, 57]]`, accuracy 97,86%,
  precision 96,61%, recall 98,28% e F1 97,44% para oportunidade.
- [ ] Implementar agregação de probabilidades dos chunks para a reunião.
- [x] Validar inferência local na RTX 3050 com PyTorch CUDA.
- [x] Documentar hardware, tempo de inferência e limitações da pseudo-rotulagem.
- [x] Documentar hardware e tempo do fine-tuning completo.
  Resultado: 104 segundos e pico de aproximadamente 2,14 GB de VRAM na RTX 3050.

## Comparação dos modelos

- [x] Criar `notebooks/08_model_comparison.ipynb`.
- [x] Comparar TF-IDF + Regressão Logística e BERTimbau no mesmo split.
  Resultado: 140 chunks pareados de 98 reuniões.
- [x] Escolher e justificar a métrica principal conforme o impacto de negócio.
  Decisão: recall de oportunidade, porque falsos negativos podem impedir que
  oportunidades comerciais cheguem ao time responsável.
- [x] Avaliar se acurácia está mascarando classes minoritárias.
  Resultado: foram comparadas métricas por classe, F1 macro e matrizes; accuracy
  não foi usada isoladamente.
- [x] Registrar resultados em `reports/metrics/model_comparison.json`.
- [x] Gerar gráficos e matrizes comparativas em `reports/figures/`.
- [x] Executar teste exato de McNemar e bootstrap agrupado por reunião.
  Resultado: `p=0,375` e intervalos de 95% que incluem zero para accuracy e F1;
  a diferença ainda não é conclusiva.
- [x] Selecionar o melhor modelo provisório do experimento atual.
  Decisão: BERTimbau, por vencer quatro das cinco métricas, reduzir os erros de
  seis para três e apresentar Brier score 0,0159 contra 0,1061 do baseline.
- [ ] Selecionar o modelo final após avaliação no conjunto humano reservado.

## Evolução do RAG

- [x] Criar um baseline simples de busca lexical.
- [x] Revisar palavras-chave com stopwords ou baixo valor semântico.
  Resultado: 19 keywords vazias/apenas stopwords foram identificadas e passam a
  ser ignoradas no índice lexical; a base original foi preservada.
- [ ] Separar fatos documentados de inferências dentro dos chunks mistos.
- [ ] Adicionar data de verificação a cada fonte/registro.
- [x] Criar aliases para produtos, módulos e concorrentes.
  Resultado: 29 grupos versionados em `data/knowledge_base/rag_aliases.json`.
- [ ] Tratar conceitos repetidos entre chunks de dor e sinal comercial.
- [x] Criar um conjunto de perguntas com documentos esperados.
  Resultado: 32 consultas e 34 relações de relevância em
  `data/knowledge_base/rag_evaluation_queries.json`.
- [x] Medir `Recall@k`, `Hit@k`, `MRR` e `nDCG` dos retrievers.
- [x] Implementar busca por embeddings com mean pooling do BERTimbau base.
- [x] Comparar busca lexical, vetorial e híbrida.
  Resultado: BM25 com aliases venceu com Recall@5 93,75%, Hit@5 96,88%,
  MRR 76,64% e nDCG@5 80,36%.
- [x] Implementar reranking considerando o nível de evidência.
  Resultado: o bônus de evidência não melhorou esta avaliação e não será o padrão.
- [x] Criar `notebooks/09_rag_retrieval_evolution.ipynb`.
- [x] Definir contrato de retrieval que sempre devolve fontes e nível de evidência.
- [x] Definir política explícita que impede documentos de hipótese de sustentarem fatos.
- [x] Testar um modelo especializado em embeddings de sentenças em português.
  Resultado: `multilingual-e5-small` venceu com Recall@5 98,44%, Hit@5 100%,
  MRR 92,19% e nDCG@5 93,47%.
- [x] Criar `notebooks/10_sentence_embeddings_retrieval.ipynb`.
- [x] Exigir fontes nas respostas comerciais produzidas pelo RAG.
- [x] Impedir que hipótese comercial seja apresentada como fato.

## Integração final

- [~] Extrair entidades, dores e sinais comerciais dos chunks das reuniões.
  Parcial: produtos, categorias, dores e sinais são estruturados a partir dos
  documentos recuperados; NER explícito sobre a transcrição ainda está pendente.
- [ ] Usar entidades extraídas por NER para consultar a base TOTVS.
- [x] Produzir insights estruturados com produto, evidência e fontes.
- [x] Agregar resultados de chunks para o nível da reunião.
  Regra provisória: ao menos dois chunks com probabilidade ≥ 0,80 e densidade
  mínima de 5%; precisa ser calibrada contra rótulos humanos.
- [x] Definir tratamento para resultados conflitantes entre chunks.
  Resultado: reuniões candidatas com ao menos dois chunks ≤ 0,20 recebem flag
  de contexto misto para revisão, sem descartar evidências.
- [x] Criar e executar `notebooks/11_final_integration.ipynb` nos 29.972 chunks.
- [ ] Criar avaliação ponta a ponta com reuniões anotadas.
- [x] Documentar limitações, riscos e próximos experimentos.
  Diagnóstico: 975 de 1.126 reuniões foram candidatas e 935 têm contexto misto;
  a taxa alta reforça que pseudo-rótulos não bastam para calibrar produção.

## Organização e reprodutibilidade

- [x] Definir e registrar dependências do ambiente Python em `requirements.txt`.
- [x] Padronizar os notebooks no kernel `Wedjat (Python 3.12 CUDA)`/`wedjat`.
- [ ] Remover caches locais antigos de Python antes do versionamento.
- [ ] Garantir que notebooks não salvem trechos sensíveis nas saídas.
- [ ] Atualizar este `TODO.md` e o `README.md` a cada etapa concluída.

## Decisões registradas

- O desenvolvimento será conduzido principalmente por notebooks documentados.
- A reunião é a unidade de negócio; chunks são unidades técnicas de processamento.
- A limpeza não remove stopwords antes dos experimentos com transformers.
- A divisão dos dados será feita por reunião para evitar vazamento entre chunks.
- O RAG complementa a classificação supervisionada, mas não substitui os dois
  algoritmos exigidos pela Sprint 3.
- O primeiro alvo supervisionado será oportunidade comercial binária no nível
  do chunk, com split agrupado por reunião.
- Os modelos comparados serão TF-IDF + Logistic Regression e BERTimbau.
- Os rótulos automáticos iniciais são pseudo-rótulos; concordância entre modelos
  não será apresentada como precisão sem uma auditoria humana.
- As métricas altas do baseline lexical podem estar infladas porque um dos
  rotuladores fracos também utiliza regras lexicais.
- Na pseudo-validação, o BERTimbau é o melhor modelo provisório pelo desempenho
  equilibrado; o baseline vence no recall e continua como referência barata.
- Se um falso negativo custar quatro ou mais revisões de falso positivo, o custo
  observado passa a favorecer o baseline; essa razão precisa ser validada pelo negócio.
- Não há seleção definitiva para produção sem o teste humano reservado.
- Para o RAG, o retriever padrão atual é `multilingual-e5-small`; obteve
  Recall@5 98,44% e superou BM25 com aliases e BERTimbau base.
- O conjunto de teste final será composto somente por exemplos com rótulos humanos.
- Os notebooks detectarão automaticamente RTX local, GPU do Colab ou CPU.
- A base TOTVS pronta para consumo fica em
  `data/knowledge_base/totvs_rag_kb_v1.json`.

## Sprint 4 — Solução integrada de inteligência comercial

Status: `ready-for-human`

### Problem Statement

A área comercial precisa transformar uma nova transcrição em indicadores úteis sem executar manualmente os notebooks, interpretar scores técnicos ou combinar resultados de modelos diferentes. A solução atual comprova os experimentos, mas ainda não oferece um ponto de entrada reutilizável que preserve a transcrição e devolva, em um único contrato, produto, sentimento, churn, oportunidade, termos e próxima ação.

### Solution

Entregar um conjunto modular de notebooks documentados, sem biblioteca nova, CLI ou interface web, que processe uma transcrição por vez. Os notebooks 12 a 17 isolam fundamentos e funcionalidades; o notebook 18 é o ponto de entrada integrado, preserva o texto original, coordena os modelos e fallbacks disponíveis, consulta a base TOTVS e exibe um JSON estruturado. Todo resultado exige revisão humana e declara os modelos, o modo de análise e o significado dos scores utilizados.

### User Stories

1. Como pessoa da área comercial, quero analisar uma transcrição diretamente no notebook, para seguir o fluxo atual do Challenge.
2. Como pessoa da área comercial, quero executar a solução em um notebook numerado e explicado, para seguir o mesmo fluxo das etapas anteriores do Challenge.
3. Como pessoa usuária do notebook, quero informar o texto em uma célula de configuração, para analisar uma nova reunião sem alterar o pipeline.
4. Como pessoa usuária do notebook, quero carregar uma transcrição de arquivo texto, para analisar registros já salvos.
5. Como pessoa usuária do notebook, quero carregar uma transcrição de JSON, para integrar exportações estruturadas.
6. Como pessoa usuária do notebook, quero visualizar as labels e o JSON em células de resultado, para revisar a análise dentro do ambiente atual do projeto.
7. Como revisora comercial, quero que a transcrição original permaneça inalterada no resultado, para conferir as labels contra a fonte.
8. Como revisora comercial, quero receber um produto principal, para identificar rapidamente a solução TOTVS mais compatível.
9. Como revisora comercial, quero receber até três produtos candidatos ranqueados, para avaliar alternativas de cross-sell ou upsell.
10. Como revisora comercial, quero visualizar scores, termos correspondentes, documentos e fontes dos produtos, para validar o fundamento do ranking.
11. Como revisora comercial, quero uma label de sentimento positiva, neutra, negativa ou mista, para entender o tom geral da reunião.
12. Como revisora comercial, quero que sinais positivos e negativos relevantes resultem em sentimento misto, para não esconder divergências entre trechos.
13. Como gestora comercial, quero risco de churn baixo, médio ou alto, para priorizar contas que exigem atenção.
14. Como gestora comercial, quero que churn seja tratado como sinal sujeito a revisão, para não confundi-lo com cancelamento confirmado.
15. Como pessoa de pré-vendas, quero saber se uma oportunidade comercial foi detectada, para decidir se devo qualificá-la.
16. Como pessoa de pré-vendas, quero até dez termos principais, priorizando produtos, dores, concorrentes e vocabulário comercial, para compreender o contexto sem depender de uma nuvem de palavras.
17. Como pessoa da área comercial, quero uma recomendação de ação padronizada, para saber o próximo passo sugerido.
18. Como revisora comercial, quero que churn alto priorize retenção, para tratar primeiro o risco de perda.
19. Como revisora comercial, quero que sinais mistos ou de baixa confiança exijam revisão manual, para evitar ação baseada em evidência fraca.
20. Como revisora comercial, quero que oportunidade e produto confiáveis sugiram demonstração, para avançar o fluxo comercial.
21. Como revisora comercial, quero que oportunidade sem produto confiável sugira qualificação, para coletar contexto antes de ofertar.
22. Como revisora comercial, quero que todos os resultados indiquem revisão humana obrigatória, para impedir automação indevida sobre clientes.
23. Como responsável técnico, quero saber qual modelo e modo produziram cada indicador, para distinguir inferência de fallback.
24. Como responsável técnico, quero distinguir probabilidade de modelo de score heurístico, para não apresentar medidas diferentes como equivalentes.
25. Como responsável técnico, quero que a ausência de checkpoints ou dependências pesadas acione fallbacks transparentes, para manter a solução executável.
26. Como responsável técnico, quero carregar modelos apenas quando necessários, para manter a inicialização leve.
27. Como responsável técnico, quero usar artefatos locais e cache offline quando configurados, para não depender de downloads em toda execução.
28. Como pessoa usuária do notebook, quero gravar o JSON somente quando configurar um arquivo de saída, para controlar a persistência.
29. Como pessoa usuária do notebook, quero erros claros para entrada vazia, JSON inválido ou campos ausentes, para corrigir o uso sem investigar o código.
30. Como equipe do Challenge, quero testes determinísticos do contrato completo, para evoluir modelos sem quebrar a integração.

### Implementation Decisions

- A fronteira principal é a função `analisar_transcricao` definida no notebook integrado; ela recebe uma transcrição e devolve uma análise comercial estruturada.
- Toda a implementação da Sprint 4 fica distribuída nos notebooks 12 a 18, sem criar uma biblioteca ou CLI paralela.
- Cada funcionalidade possui um notebook com células pequenas e explicações; o notebook 18 contém configuração de entrada, seleção do modo, execução, visualização das labels e persistência opcional do JSON.
- Uma execução aceita exatamente uma transcrição.
- O resultado inclui a transcrição original, sem normalização destrutiva.
- O processamento pode usar uma cópia normalizada internamente.
- A análise de sentimento usa Pysentimiento no modo completo e agrega chunks para produzir `positivo`, `neutro`, `negativo` ou `misto`.
- A análise de churn usa MiniLM multilíngue com NLI zero-shot no modo completo e produz `baixo`, `medio` ou `alto`.
- O classificador BERTimbau de oportunidade é usado quando o checkpoint ajustado estiver disponível.
- O retriever E5 é usado quando modelo e índice compatíveis estiverem disponíveis; BM25 com aliases é o fallback de produtos.
- Componentes de modelo são carregados sob demanda e implementam interfaces substituíveis.
- Fallbacks lexicais auditáveis mantêm a execução funcional e são declarados como heurísticos.
- O produto principal é o primeiro de até três candidatos ranqueados.
- Candidatos carregam score, tipo de score, termos correspondentes, documentos e URLs das fontes.
- Sentimento, churn e oportunidade carregam label, score, tipo de score, mecanismo e modelo utilizado.
- Scores zero-shot ou heurísticos não são descritos como probabilidades calibradas de negócio.
- A recomendação segue a prioridade: retenção; revisão manual; demonstração; qualificação; acompanhamento.
- O resultado sempre sinaliza que revisão humana é obrigatória.
- A serialização JSON usa labels estáveis em português sem acentos para facilitar integração.
- Falhas de configuração de um modelo provocam fallback apenas no modo automático; o resultado registra a causa sem incluir conteúdo sensível adicional.

### Testing Decisions

- Os testes são separados por funcionalidade, executam as células testáveis dos notebooks na ordem e atravessam a função `analisar_transcricao`, recebendo uma transcrição e validando o resultado estruturado.
- Testes observam comportamento externo, não detalhes internos de tokenização, pesos ou bibliotecas.
- Adaptadores de modelos externos são substituídos por dublês determinísticos nos testes unitários.
- O contrato completo cobre preservação da entrada, todas as labels, ranking de produtos, termos, recomendação, revisão humana e metadados.
- Casos de borda cobrem entrada vazia, sinais mistos, churn prioritário, ausência de produto, indisponibilidade de modelo e fontes ausentes.
- Os notebooks são validados estruturalmente, limitam células de código extensas e têm suas células testáveis executadas diretamente pelos testes automatizados.
- Smoke tests de modelos reais são opcionais e executados somente quando dependências e checkpoints estiverem instalados.
- O projeto não possui testes de integração anteriores; esta Sprint estabelece a fronteira pública como seam principal.

### Out of Scope

- Interface web ou aplicativo gráfico.
- Interface de linha de comando como entrega da Sprint 4.
- Nova biblioteca ou pacote de aplicação em `src/`.
- Transcrição de áudio ou captura de reuniões em tempo real.
- Dashboard de pipeline, alertas e notificações.
- Sincronização ou escrita no CRM.
- Preenchimento completo dos campos SPICED.
- Envio automático de mensagens, propostas ou descontos.
- Treinamento de novos modelos ou apresentação de métricas como validadas sem rótulos humanos.
- Processamento em lote de várias transcrições numa única execução.

### Further Notes

- O Pysentimiento foi treinado em textos de redes sociais; a adequação a reuniões comerciais precisa de avaliação humana.
- O MiniLM NLI não foi treinado para churn; sua saída é um sinal zero-shot para revisão.
- Os artefatos BERTimbau e E5 existentes permanecem opcionais porque não estão versionados.
- A base TOTVS versionada é a fonte de grounding para identificação de produtos.
- A solução é apoio à inteligência comercial e não substitui o CRM nem a decisão humana.

### Progresso de implementação

- [x] Definir o contrato da análise comercial e a fronteira pública no notebook.
- [x] Implementar carregamento e validação de uma transcrição por execução.
- [x] Implementar identificação e ranking de produtos com fontes.
- [x] Integrar E5 local e fallback BM25 com aliases para produtos.
- [x] Integrar Pysentimiento e fallback de sentimento.
- [x] Integrar MiniLM zero-shot e fallback de churn.
- [x] Integrar BERTimbau e fallback de oportunidade.
- [x] Extrair até dez termos principais.
- [x] Implementar recomendação de ação e revisão humana obrigatória.
- [x] Modularizar a Sprint 4 nos notebooks 12 a 18 e separar os testes por funcionalidade.
- [x] Criar notebook numerado para texto direto, arquivo texto, JSON e persistência opcional.
- [x] Documentar instalação, modelos opcionais e exemplos de uso.
- [x] Executar testes, revisão de código e validação ponta a ponta.
  Resultado: 31 testes determinísticos aprovados, incluindo persistência do JSON,
  documentos sem fonte, fallbacks transparentes e erros de inferência não ocultados.
