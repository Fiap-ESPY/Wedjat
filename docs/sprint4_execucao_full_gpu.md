# Reproduzir a Sprint 4 em um PC com GPU

Este roteiro conclui a parte que depende dos modelos reais. O notebook 18 já foi executado em `fallback` com uma transcrição sintética. A execução `full` ainda precisa ser feita em um computador com recursos suficientes. Ela não substitui a validação com rótulos humanos.

## 1. Preparar o ambiente

Use Python 3.12 e crie um ambiente virtual na raiz do projeto:

```bash
python -m venv .venv
```

Ative o ambiente (`source .venv/bin/activate` no Linux/macOS, `.venv\Scripts\activate.bat` no CMD ou `.venv\Scripts\Activate.ps1` no PowerShell). Instale o PyTorch com o comando correspondente ao sistema e à versão CUDA da GPU no [seletor oficial do PyTorch](https://pytorch.org/get-started/locally/). Em seguida:

```bash
python -m pip install -r requirements.txt
python -m pip check
python -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'sem CUDA')"
```

Se `torch.cuda.is_available()` for `False`, confira driver, CUDA e a variante instalada do PyTorch antes de iniciar o treino. A versão do PyTorch depende do hardware, por isso não está fixada em `requirements.txt`. Os outros pacotes seguem as versões do projeto. Para referência sobre o carregamento de modelos, consulte a [documentação oficial do Transformers](https://huggingface.co/docs/transformers/installation).

## 2. Gerar os artefatos na ordem

Abra o Jupyter na raiz do projeto e execute integralmente, nesta ordem:

1. `notebooks/03_tokenizacao_e_chunks.ipynb` → `data/processed/chunks_bertimbau.jsonl`.
2. `notebooks/05_supervisao_fraca_e_divisao.ipynb` → pseudo-rótulos e fila reservada de auditoria.
3. `notebooks/07_treinamento_bertimbau.ipynb` → `data/processed/bertimbau_opportunity_best/`.
4. `notebooks/10_busca_embeddings_e5.ipynb` → `data/processed/rag_multilingual_e5_small_embeddings.npz`.

Os notebooks baixam BERTimbau e E5 quando não estão no cache. O modo `full` também usa os modelos de sentimento e de NLI para churn. Estes artefatos e caches ficam fora do Git. Preserve os relatórios versionados existentes se quiser compará-los com a nova execução, pois os notebooks de treino podem reescrever métricas e figuras locais.

Confira os dois artefatos exigidos pelo notebook 18:

```bash
python -c "from pathlib import Path; paths=[Path('data/processed/bertimbau_opportunity_best/config.json'), Path('data/processed/rag_multilingual_e5_small_embeddings.npz')]; print([(str(p), p.exists()) for p in paths]); assert all(p.exists() for p in paths)"
```

## 3. Executar e conferir o protótipo

Abra `notebooks/18_analise_comercial.ipynb` e, na célula **Configurar a entrada**, use inicialmente uma transcrição sintética:

```python
FONTE_ENTRADA = "texto"
TRANSCRICAO_DIRETA = "Usamos Protheus e queremos avaliar uma proposta para implantar um ERP."
ARQUIVO_ENTRADA = None
CAMPO_JSON = "transcricao"
MODO_ANALISE = "full"
ARQUIVO_SAIDA = None
```

Execute todas as células de cima para baixo. O resultado deve mostrar `analysis_mode.requested == "full"`, todos os quatro componentes em `"model"`, tabela de indicadores com tipos de score, fontes dos produtos, critérios e motivo da recomendação e tempo de análise. Confira o JSON completo antes de usar uma transcrição real. Se ocorrer erro, registre o traceback e as versões de Python, PyTorch, Transformers e Pysentimiento; não mude silenciosamente para `auto` ao relatar uma execução `full`.

Para o relatório da Sprint 4, registre apenas data, versões, GPU, tempo, mecanismos, tipos de score e se houve erro. Não copie o texto nem IDs de reuniões para um relatório público. A seleção BERTimbau/E5, suas métricas experimentais e os limites estão em [`reports/sprint4_conclusao.md`](../reports/sprint4_conclusao.md).

## 4. Testes e avaliação ainda pendentes

Execute os testes determinísticos com `python -m unittest discover -s tests -q`. Em seguida, obtenha rótulos humanos para a fila de 150 chunks reservados e reuniões realmente inéditas, separando calibração e teste por ID de reunião. Compare TF-IDF e BERTimbau no mesmo teste humano; revise produto principal, sentimento, risco de churn, oportunidade e recomendação com a área comercial. Só então calcule métricas de qualidade ou ajuste limiares.
