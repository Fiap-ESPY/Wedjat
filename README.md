# Wedjat

O Wedjat transforma transcrições extensas de reuniões em dados preparados para
experimentos de classificação e extração de insights de negócio.

## Tratamento inicial das reuniões

O primeiro estágio está implementado em
`src/wedjat/data/meetings.py`. Ele:

1. lê o arquivo NDJSON em streaming, sem carregar todas as transcrições na memória;
2. valida `ID_MEETING` e `ANON_TRANSCRICAO`;
3. normaliza apenas espaços e quebras de linha, sem remover palavras;
4. remove duplicatas exatas pelo identificador da reunião;
5. interrompe o processamento se um mesmo ID possuir conteúdos diferentes;
6. acrescenta contagens de caracteres e turnos de locutor;
7. gera um resumo sem copiar transcrições para logs ou relatórios.

A entrada e as saídas são definidas em `configs/data_preparation.json`.

Para executar a partir da raiz do projeto:

```powershell
python src/wedjat/data/meetings.py
```

Saídas:

- `data/processed/meetings.jsonl`: uma reunião única por linha;
- `reports/metrics/data_preparation_summary.json`: auditoria numérica do processo.

Para executar os testes:

```powershell
python -m unittest discover -s tests -v
```

