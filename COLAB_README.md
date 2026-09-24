# Execução do Wedjat no Google Colab

Este guia usa os arquivos do repositório para reproduzir o projeto a partir
das transcrições anonimizadas. O arquivo `data/processed/meetings.jsonl` é
versionado; os demais artefatos são gerados pelos notebooks.

## Atenção aos dados

`data/raw/ANON_transcricao.json` e `data/processed/meetings.jsonl` são
versionados neste projeto. Os demais artefatos gerados permanecem locais.

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

Abra `notebooks/00_projeto_completo_colab.ipynb` e use **Runtime > Run all**.
Ele reúne todo o conteúdo dos notebooks 01 a 11, explica cada etapa e libera
objetos grandes entre os modelos para controlar o uso de memória da GPU.

Na primeira célula de configuração, o caminho padrão é
`/content/Wedjat-Colab`. Se você descompactar o pacote em outro lugar, ajuste a
variável `PROJECT_DIR`.

## Ordem original das etapas

O notebook único executa internamente a seguinte ordem:

Execute os notebooks integralmente nesta ordem:

1. `01_preparacao_dados.ipynb`
2. `02_base_conhecimento_rag.ipynb`
3. `03_tokenizacao_e_chunks.ipynb`
4. `04_alvo_e_bertimbau.ipynb`
5. `05_supervisao_fraca_e_divisao.ipynb`
6. `06_baseline_oportunidade.ipynb`
7. `07_treinamento_bertimbau.ipynb`
8. `08_comparacao_modelos.ipynb`
9. `09_evolucao_busca_rag.ipynb`
10. `10_busca_embeddings_e5.ipynb`
11. `11_integracao_reunioes.ipynb`

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
