# Conclusão da Sprint 4 — análise comercial

## Escolha para o protótipo

A interface do protótipo é `analisar_transcricao` no notebook 18. No caminho com modelos, ela usa BERTimbau ajustado para oportunidade e `intfloat/multilingual-e5-small` para recuperar documentos de produto. A escolha **não é uma seleção validada para produção**: a avaliação do classificador usou pseudo-rótulos, a avaliação de recuperação usou consultas curadas da própria base e não há rótulos humanos de produto, sentimento, churn ou recomendação.

A prioridade de negócio registrada no experimento é *recall* de oportunidade: perder uma oportunidade pode custar mais que revisar um falso positivo. Nesse critério isolado, TF-IDF + Regressão Logística venceu: recall 1,000 contra 0,983 do BERTimbau, com zero contra um falso negativo. Para a demonstração com modelo, BERTimbau foi mantido porque teve F1 de oportunidade 0,974 contra 0,951, 3 erros contra 6 nos mesmos 140 chunks, precisão 0,966 contra 0,906 e Brier 0,016 contra 0,106. A diferença de acertos não é conclusiva (McNemar exato p = 0,375; intervalos bootstrap para as principais diferenças incluem zero). O baseline é muito mais leve: 0,69 MB e 0,39 s de ajuste, ante 415,54 MB e 93,66 s. Se um falso negativo custar mais que quatro revisões de falso positivo, a comparação operacional registrada favorece o baseline. Sem custos reais e avaliação humana, não há argumento para descartar o baseline.

Para busca, o E5 alcançou Recall@5 de 0,984 e MRR de 0,922, contra 0,938 e 0,766 de BM25 com aliases em 32 consultas curadas. Por isso, E5 é o retriever do caminho `full`; BM25 permanece o fallback executável. Os números completos estão em [`model_comparison.json`](metrics/model_comparison.json) e [`sentence_embeddings_retrieval.json`](metrics/sentence_embeddings_retrieval.json).

## O que foi verificado

O fluxo apresentado é **Transcrição → Processamento → Modelo ou fallback → Indicadores → Recomendação**. Cada resultado registra labels, mecanismo, tipo de score, fontes de produto, critérios e motivo da ação. A recomendação exige revisão humana. O notebook 18 separa entrada, análise, tabela de indicadores, recomendação, JSON e persistência opcional.

Os testes determinísticos verificam o contrato e a prioridade das recomendações com transcrições sintéticas. O smoke test anterior processou 20 reuniões da base histórica no modo `fallback`, com zero falhas de contrato e fontes em todos os produtos candidatos retornados. Esse teste é de execução, não mede acurácia. A base recebida tem 1.174 registros, 1.126 reuniões únicas e 48 duplicatas exatas; ela coincide em agregados com a base já usada no projeto e não comprova avaliação em reuniões inéditas. Consulte [`sprint4_existing_data_smoke.json`](metrics/sprint4_existing_data_smoke.json).

## Limitações e próximos passos

- Os modelos de sentimento e churn são sinais de triagem, não probabilidades calibradas para reuniões comerciais. Não há rótulos humanos para aferir esses indicadores ou a utilidade da ação sugerida.
- O ranking de produto pode trazer um documento comparativo antes do produto citado na transcrição; a fonte e o produto principal devem ser conferidos durante a revisão humana.
- Nesta máquina faltam PyTorch, Transformers e Pysentimiento, além do checkpoint local BERTimbau e do índice E5. Uma sondagem real do modo `full` retornou `RuntimeError: O modo full exige o modelo e o índice E5.` Não há demonstração `full` reproduzida neste ambiente.
- Para concluir a validação, executar notebooks 03, 05, 07 e 10 em ambiente com as dependências e artefatos, rodar o notebook 18 em `full`, obter rótulos humanos para a fila de 150 chunks reservados e avaliar em reuniões inéditas separadas por ID. Comparar classificadores no mesmo teste humano e revisar produto, sentimento, churn, oportunidade e ação com a área comercial antes de calibrar limiares.
