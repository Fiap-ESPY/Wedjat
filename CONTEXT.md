# Inteligência comercial Wedjat

O Wedjat transforma uma nova transcrição de reunião em indicadores estruturados para apoiar a revisão da área comercial, sem tomar decisões automáticas sobre clientes.

## Language

**Transcrição**:
Texto original de uma reunião fornecido como entrada para uma análise; é preservado sem alterações destrutivas junto ao resultado.
_Avoid_: Reunião, documento bruto

**Análise comercial**:
Conjunto estruturado de indicadores derivados de uma transcrição.
_Avoid_: Diagnóstico, decisão automática

**Produto principal**:
Produto TOTVS mais compatível com as necessidades encontradas na transcrição.
_Avoid_: Produto recomendado, produto vendido

**Produto candidato**:
Produto TOTVS ranqueado como possível correspondência, acompanhado de score e fontes da base de conhecimento.
_Avoid_: Oferta confirmada

**Revisão humana**:
Validação obrigatória dos indicadores e da recomendação por uma pessoa da área comercial antes de qualquer ação sobre o cliente.
_Avoid_: Aprovação automática

**Modo de análise**:
Identificação transparente dos mecanismos usados para produzir os indicadores, incluindo o uso dos modelos treinados ou de fallback lexical.
_Avoid_: Modo de execução

**Sentimento**:
Percepção geral da linguagem da transcrição, classificada como positiva, neutra, negativa ou mista.
_Avoid_: Satisfação do cliente

**Risco de churn**:
Sinal comercial de possibilidade de perda do cliente, classificado como baixo, médio ou alto; não representa uma previsão confirmada de cancelamento.
_Avoid_: Churn, cancelamento confirmado

**Oportunidade comercial**:
Sinal de necessidade que pode ser atendida comercialmente, classificado como detectada ou não detectada.
_Avoid_: Venda, negócio fechado

**Termo principal**:
Termo relevante da transcrição que representa produto, dor, concorrente ou vocabulário comercial.
_Avoid_: Palavra frequente

**Recomendação de ação**:
Próximo passo sugerido para avaliação durante a revisão humana, expresso por uma label controlada.
_Avoid_: Ação automática, decisão comercial

**SPICED**:
Estrutura de qualificação comercial formada por Situação, Dor, Impacto, Evento Crítico e Decisão.
_Avoid_: Questionário fixo, score de sentimento

**Oportunidade de cross-sell ou upsell**:
Necessidade não atendida que pode corresponder a outro produto ou ampliação do portfólio TOTVS; permanece uma sugestão até a revisão humana.
_Avoid_: Venda confirmada, oferta automática
