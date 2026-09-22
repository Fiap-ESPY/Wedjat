# Modelos para sentimento e risco de churn

Pesquisa realizada para a Sprint 4 do Wedjat. O objetivo é escolher modelos que funcionem em português, preservem o contrato de labels e deixem explícitas as limitações de domínio.

## Conclusão recomendada

- **Sentimento:** usar `pysentimiento/bertweet-pt-sentiment` como padrão do modo completo. Ele foi ajustado especificamente para polaridade em português e devolve `POS`, `NEG` e `NEU`. Como não possui a classe `misto`, o Wedjat deve classificar os chunks e agregar como `misto` quando houver apoio relevante simultâneo para positivo e negativo.
- **Risco de churn:** usar `MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli` em classificação zero-shot com hipóteses em português para `baixo`, `medio` e `alto`. O score indica preferência do modelo entre as hipóteses; não é uma probabilidade calibrada de cancelamento.
- **Evolução:** quando houver transcrições comerciais rotuladas, ajustar o BERTimbau separadamente para sentimento e churn. O BERTimbau base não é, por si só, um classificador de sentimento.
- **Fallback:** se Transformers, PyTorch ou os checkpoints não estiverem disponíveis localmente, manter regras lexicais auditáveis e identificar o resultado como heurístico.

## Alternativas avaliadas

### BERTimbau com fine-tuning próprio

O checkpoint `neuralmind/bert-base-portuguese-cased` é um BERT de 110 milhões de parâmetros pré-treinado em português brasileiro. Seu model card apresenta uso para representação e *fill-mask*, não uma cabeça pronta para sentimento. Portanto, ele só é uma alternativa correta depois de fine-tuning com dados rotulados para a tarefa. [Model card oficial do BERTimbau](https://huggingface.co/neuralmind/bert-base-portuguese-cased)

O TweetSentBR oferece 15 mil tweets em português brasileiro anotados para sentimento e pode apoiar um experimento inicial, mas seu domínio é televisão/Twitter, não reuniões comerciais. O melhor conjunto futuro continua sendo transcrição comercial anotada pelo próprio projeto. [Artigo do TweetSentBR na ACL Anthology](https://aclanthology.org/L18-1658/)

**Vantagem:** mantém a família de modelos já usada no Challenge e pode se adaptar ao domínio.

**Limitação atual:** o repositório não possui rótulos humanos de sentimento ou churn suficientes para esse treinamento.

### Pysentimiento em português

`pysentimiento/bertweet-pt-sentiment` usa o BERTabaporu, um RoBERTa treinado em tweets portugueses, e expõe diretamente as classes `POS`, `NEG` e `NEU`. O artefato principal em `safetensors` tem aproximadamente 540 MB. [Model card oficial](https://huggingface.co/pysentimiento/bertweet-pt-sentiment) e [repositório oficial do pysentimiento](https://github.com/pysentimiento/pysentimiento)

**Vantagem:** português específico, contrato de labels pronto e integração direta com Transformers/pysentimiento.

**Limitação:** foi treinado em linguagem de redes sociais; precisa ser avaliado em reuniões e pode interpretar mal linguagem corporativa, ironia ou falas de participantes diferentes.

### XLM-RoBERTa multilíngue para sentimento

`cardiffnlp/twitter-xlm-roberta-base-sentiment` foi treinado em cerca de 198 milhões de tweets e ajustado para sentimento em oito idiomas, incluindo português. [Model card oficial do Cardiff NLP](https://huggingface.co/cardiffnlp/twitter-xlm-roberta-base-sentiment)

**Vantagem:** checkpoint amplamente multilíngue e pronto para `text-classification`.

**Limitação:** continua especializado em Twitter e é mais amplo do que o necessário para uma solução somente em português. Por isso fica como segunda opção, não como padrão.

### NLI multilíngue para churn zero-shot

`MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli` foi ajustado em MNLI/XNLI para inferência textual e seu model card o indica para classificação zero-shot em mais de cem idiomas. Tem seis camadas, licença MIT declarada e prioriza velocidade em relação às variantes maiores. [Model card oficial](https://huggingface.co/MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli)

O pipeline zero-shot transforma cada label em uma hipótese e usa o logit de implicação do modelo NLI. Isso permite testar labels de churn sem conjunto de treino próprio, mas não converte sentimento negativo em churn nem produz risco calibrado. [Implementação oficial do pipeline Transformers](https://github.com/huggingface/transformers/blob/main/src/transformers/pipelines/zero_shot_classification.py)

**Vantagem:** modelo compacto para uma primeira classificação model-based de churn e substituível sem mudar a API.

**Limitação:** não foi treinado em churn de clientes. A label sempre deve exigir revisão humana e ser reavaliada quando houver dados rotulados.

Para priorizar qualidade em uma máquina com mais recursos, `MoritzLaurer/mDeBERTa-v3-base-mnli-xnli` é a alternativa maior indicada pelo próprio autor do MiniLM. [Model card oficial do mDeBERTa](https://huggingface.co/MoritzLaurer/mDeBERTa-v3-base-mnli-xnli)

## Implicações para o Wedjat

1. Transcrições longas devem ser divididas em chunks respeitando o limite do tokenizer de cada modelo.
2. O resultado de sentimento é agregado no nível da transcrição; conflito relevante entre chunks positivos e negativos produz `misto`.
3. O resultado de churn é um sinal para revisão, nunca uma confirmação de cancelamento.
4. Checkpoints devem ser carregados sob demanda e poder usar cache local/offline.
5. O JSON deve declarar modelo, modo e tipo de score para cada indicador.
6. Antes de apresentar métricas de qualidade, os dois modelos precisam ser avaliados em transcrições comerciais anotadas por pessoas.
