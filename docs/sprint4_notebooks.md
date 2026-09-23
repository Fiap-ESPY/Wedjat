# Sprint 4 — análise comercial em notebooks

O ponto de entrada é `notebooks/18_sprint4_commercial_analysis.ipynb`. Ele
carrega os módulos anteriores no mesmo kernel, processa exatamente uma
transcrição e apresenta um JSON para revisão humana. Não há CLI, biblioteca de
aplicação ou interface web.

## Organização

| Notebook | Responsabilidade |
| --- | --- |
| `12_sprint4_foundation.ipynb` | Normalização interna, tokens e catálogo TOTVS. |
| `13_sprint4_products_and_terms.ipynb` | Ranking de até três produtos e até dez termos. |
| `14_sprint4_sentiment.ipynb` | Pysentimiento e fallback lexical. |
| `15_sprint4_churn.ipynb` | MiniLM zero-shot e fallback lexical. |
| `16_sprint4_opportunity.ipynb` | BERTimbau ajustado e fallback comercial. |
| `17_sprint4_recommendation.ipynb` | Prioridade da próxima ação e revisão humana. |
| `18_sprint4_commercial_analysis.ipynb` | Entrada, integração, visualização e saída opcional. |

O notebook 18 deve ser executado de cima para baixo. Os notebooks 12 a 17 são
módulos explicativos e também podem ser abertos para estudar cada indicador.

## Instalação

Use Python 3.12 e instale primeiro o PyTorch compatível com a CPU ou com a versão
CUDA da máquina. Em seguida:

```bash
pip install -r requirements.txt
jupyter notebook
```

`pysentimiento==0.7.3` é a versão publicada atualmente no PyPI. Ela declara
Python `>=3.8,<4`, PyTorch `>=2` e Transformers `>=4.13`. O projeto mantém o
PyTorch sem versão fixa porque a distribuição correta depende do hardware.

Fontes oficiais: [pysentimiento no PyPI](https://pypi.org/project/pysentimiento/),
[dependências do projeto](https://github.com/pysentimiento/pysentimiento/blob/master/pyproject.toml)
e [modelo português](https://huggingface.co/pysentimiento/bertweet-pt-sentiment).

## Modos de análise

| Modo | Comportamento |
| --- | --- |
| `auto` | Tenta os modelos e usa fallback quando uma dependência ou checkpoint está indisponível. |
| `full` | Exige os modelos de sentimento, churn e oportunidade; falha com mensagem clara se algum não puder ser carregado. |
| `fallback` | Não carrega modelos pesados e usa somente mecanismos lexicais auditáveis. |

O resultado registra o modo solicitado, o mecanismo usado por indicador e o
tipo do score. `model_probability` e `heuristic` não são tratados como medidas
equivalentes.

## Modelos e artefatos

| Indicador | Caminho preferencial | Fallback e limitação |
| --- | --- | --- |
| Produto | `intfloat/multilingual-e5-small` com o índice produzido pelo notebook 10. | BM25 com aliases; similaridade e score heurístico não são probabilidade de compra. |
| Sentimento | `pysentimiento/bertweet-pt-sentiment`. | Regras lexicais; o modelo foi treinado em redes sociais, não em reuniões. |
| Risco de churn | `MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli`. | Regras lexicais; o modelo NLI não foi treinado para prever churn. |
| Oportunidade | `data/processed/bertimbau_opportunity_best`. | Regras de intenção, compra, dor e produto; o checkpoint usa pseudo-rótulos. |

O checkpoint de oportunidade é produzido pelo notebook 07 e fica fora do Git.
O índice E5 é produzido pelo notebook 10 em
`data/processed/rag_multilingual_e5_small_embeddings.npz` e também fica fora do
Git. Sem esses artefatos, o modo `auto` continua com fallback; o modo `full`
interrompe a execução. Os modelos do Hugging Face são carregados sob demanda e
ficam no cache local após o primeiro download.

Para escolher outro cache, configure `HF_HOME` antes de iniciar o Jupyter. Para
impedir acesso de rede e usar somente arquivos já armazenados, configure
`HF_HUB_OFFLINE=1`. Se um modelo não estiver no cache, `auto` registra o fallback
e `full` apresenta o erro. Consulte a
[documentação oficial de instalação do Transformers](https://huggingface.co/docs/transformers/installation)
e as [variáveis do Hugging Face Hub](https://huggingface.co/docs/huggingface_hub/main/package_reference/environment_variables).

## Entrada

Na célula **Configurar a entrada** do notebook 18, escolha uma única fonte.

Texto direto:

```python
FONTE_ENTRADA = "texto"
TRANSCRICAO_DIRETA = "Cliente precisa integrar estoque e faturamento."
ARQUIVO_ENTRADA = None
CAMPO_JSON = "transcricao"
MODO_ANALISE = "auto"
ARQUIVO_SAIDA = None
```

Arquivo `.txt`:

```python
FONTE_ENTRADA = "arquivo"
ARQUIVO_ENTRADA = Path("data/minha_reuniao.txt")
CAMPO_JSON = "transcricao"  # ignorado para .txt
```

Arquivo `.json` com uma única transcrição:

```json
{
  "transcricao": "Texto original da reunião"
}
```

```python
FONTE_ENTRADA = "arquivo"
ARQUIVO_ENTRADA = Path("data/minha_reuniao.json")
CAMPO_JSON = "transcricao"
```

Para exportações do Challenge, `CAMPO_JSON` também pode ser
`"ANON_TRANSCRICAO"`. O notebook rejeita listas, entrada vazia, JSON inválido,
campo ausente e configuração simultânea de texto e arquivo.

## Saída e persistência

O JSON contém a transcrição original, labels, scores, tipo de score, mecanismos,
produto principal, até três candidatos com fontes, até dez termos e a
recomendação. `revisao_humana` é sempre `true`.

Por padrão, nada é gravado:

```python
ARQUIVO_SAIDA = None
```

Para persistir explicitamente:

```python
ARQUIVO_SAIDA = Path("reports/minha_analise.json")
```

O arquivo inclui a transcrição original e deve ser tratado como dado sensível.
Não o versione nem o compartilhe sem aplicar a política de privacidade do
projeto.

## Verificação automatizada

Os testes são separados por funcionalidade e executam as células marcadas como
`wedjat-core` na mesma ordem do notebook integrado:

```bash
python -m unittest discover -s tests -v
```

Os modelos externos são substituídos por dublês determinísticos na suíte. Testes
reais dos checkpoints continuam opcionais porque exigem downloads, GPU e
artefatos locais não versionados.
