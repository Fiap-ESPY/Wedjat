# Execução do Wedjat no Google Colab

Este pacote contém os arquivos necessários para reproduzir o projeto a partir
das transcrições anonimizadas. O diretório `data/processed/` começa vazio porque
seus arquivos são gerados pelos notebooks.

## Atenção aos dados

`data/raw/ANON_transcricao (2).json` contém transcrições anonimizadas. Mesmo sem
nomes explícitos, trate o arquivo como sensível: não publique o ZIP, não deixe o
runtime compartilhado e mantenha o Google Drive com acesso restrito.

## Preparação do Colab

1. Faça upload do ZIP para uma pasta privada do Google Drive ou para a sessão.
2. Descompacte o arquivo e entre na pasta `Wedjat-Colab`.
3. No Colab, selecione **Runtime > Change runtime type > GPU**.
4. Instale as dependências:

```python
%cd /content/Wedjat-Colab
%pip install -r requirements.txt
```

Se o ZIP estiver no Google Drive, monte o Drive e ajuste o caminho do `%cd`.
O PyTorch é fornecido pelo runtime do Colab e, por isso, não é fixado no
`requirements.txt`.

## Execução recomendada: notebook único

Abra `notebooks/Wedjat_Projeto_Completo_Colab.ipynb` e use **Runtime > Run all**.
Ele reúne todo o conteúdo dos notebooks 01 a 11, explica cada etapa e libera
objetos grandes entre os modelos para controlar o uso de memória da GPU.

Na primeira célula de configuração, o caminho padrão é
`/content/Wedjat-Colab`. Se você descompactar o pacote em outro lugar, ajuste a
variável `PROJECT_DIR`.

## Ordem original das etapas

O notebook único executa internamente a seguinte ordem:

Execute os notebooks integralmente nesta ordem:

1. `01_data_understanding.ipynb`
2. `02_rag_knowledge_base.ipynb`
3. `03_tokenization_and_chunking.ipynb`
4. `04_target_and_bertimbau.ipynb`
5. `05_weak_supervision_and_split.ipynb`
6. `06_baseline_tfidf_logreg.ipynb`
7. `07_bertimbau_finetuning.ipynb`
8. `08_model_comparison.ipynb`
9. `09_rag_retrieval_evolution.ipynb`
10. `10_sentence_embeddings_retrieval.ipynb`
11. `11_final_integration.ipynb`

Os checkpoints `neuralmind/bert-base-portuguese-cased` e
`intfloat/multilingual-e5-small` são baixados na primeira execução. Os notebooks
detectam CUDA automaticamente e usam CPU como fallback, embora os notebooks 07
e 11 sejam significativamente mais rápidos com GPU.

## Principais resultados esperados

- 1.126 reuniões após deduplicação;
- 29.972 chunks;
- comparação entre TF-IDF + Regressão Logística e BERTimbau;
- E5 com Recall@5 de aproximadamente 98,44% na avaliação inicial do RAG;
- `data/processed/meeting_commercial_insights.jsonl` ao final.

As métricas supervisionadas atuais usam pseudo-rótulos. A avaliação definitiva
continua dependendo da auditoria humana reservada.
