# ExtractionAPI Dashboard

Pipeline de dados em camadas (medallion: **Bronze → Silver → Gold**) que extrai
endereços de CEP da API pública [ViaCEP](https://viacep.com.br/), processa, agrega métricas
e serve um dashboard local.

## Arquitetura

```
extracao_bronze.py        →   Camada Bronze    (dados brutos da API, arquivados por timestamp)
processamento_silver.py   →   Camada Silver    (limpeza, padronização, linhagem, dedup por CEP)
processamento_gold.py    →   Camada Gold      (agregados: distribuição por região/UF/cidade/ddd)
dashboard_server.py      →   Servidor HTTP    (serve o dashboard + arquivos do datalake)
index.html               →   Dashboard        (Chart.js, tabela Silver, métricas Gold)
```

Os dados são persistidos em `./datalake/`:

- `datalake/bronze/`  — JSON bruto por execução (`dados_cep_YYYYMMDD_HHMMSS.json`)
- `datalake/silver/`  — JSON limpo por CEP (`cep_XXXXX.json`) + `consolidado_ceps.csv`
- `datalake/gold/`    — métricas agregadas (`relatorio_metricas.json` e um por dimensão)

## Pré-requisitos

- Python 3.10+ (desenvolvido/testado com 3.14)

## Instalação

```bash
python -m venv venv

# Linux/macOS
source venv/bin/activate
# Windows (PowerShell)
venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

> Observação: o `requirements.txt` **deve** estar em UTF-8 (sem BOM). Em sistemas
> que compartilham com Linux/Docker, evite gerá-lo com `Out-File` no PowerShell,
> que usa UTF-16 por padrão. Prefira:
> `pip freeze > requirements.txt` (cmd) ou `{ pip freeze } | Set-Content requirements.txt -Encoding utf8`.

## Execução (nesta ordem)

```bash
python extracao_bronze.py       # 1. Extrai um CEP da API ViaCEP para a camada Bronze
python processamento_silver.py # 2. Limpa, padroniza e deduplica → Silver
python processamento_gold.py   # 3. Calcula agregados → Gold
python dashboard_server.py     # 4. Sobe o servidor e abre http://localhost:8000
```

## Notas

- Atualmente a Bronze extrai um único CEP fixo em `extracao_bronze.py`. Para escalar,
  substitua a constante `url_api` por uma iteração sobre uma lista/CSV de CEPs.
- O reprocessamento da Silver é idempotente quanto ao conjunto: a cada execução
  ela lê toda a Bronze e mantém o registro mais recente por CEP (deduplicação
  por data de extração embutida no nome do arquivo).
- O `dashboard_server.py` serve o diretório raiz; em ambientes compartilhados,
  considere restringir para `index.html` + `datalake/`.
