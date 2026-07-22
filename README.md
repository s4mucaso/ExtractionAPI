# ViaCEP Medallion Data Pipeline

A local end-to-end data pipeline that extracts Brazilian postal code data from the public ViaCEP API, processes it through Bronze, Silver and Gold layers, and presents the resulting information in an interactive dashboard.

The project was built to demonstrate fundamental Data Engineering concepts, including API ingestion, data lake organization, data cleaning, deduplication, lineage, aggregation and data visualization.

## Project overview

The pipeline follows the Medallion Architecture:

```text
ViaCEP API
    |
    v
Bronze Layer
Raw JSON data stored by extraction timestamp
    |
    v
Silver Layer
Cleaned, standardized and deduplicated postal code data
    |
    v
Gold Layer
Aggregated metrics by region, state, city and area code
    |
    v
Local Dashboard
Charts, indicators and processed data visualization
```

## Architecture

### Bronze layer

The Bronze layer preserves the raw response received from the ViaCEP API.

Each execution generates a new timestamped JSON file:

```text
datalake/bronze/dados_cep_YYYYMMDD_HHMMSS.json
```

This preserves the original source data and creates a basic extraction history.

### Silver layer

The Silver layer reads the Bronze files and prepares the data for analysis.

Its responsibilities include:

* Data cleaning
* Field standardization
* Postal code validation
* Addition of lineage metadata
* Deduplication by postal code
* Selection of the most recent record
* Creation of a consolidated CSV dataset

Main output:

```text
datalake/silver/consolidado_ceps.csv
```

Individual processed JSON files are also generated for each postal code.

### Gold layer

The Gold layer reads the consolidated Silver dataset and generates analytical metrics.

The current aggregations include:

* Number of postal codes by region
* Number of postal codes by state
* Number of postal codes by city
* Number of postal codes by area code
* Total number of processed records

Main output:

```text
datalake/gold/relatorio_metricas.json
```

Additional JSON files are generated for each analytical dimension.

## Dashboard

The project includes a local dashboard built with HTML, JavaScript and Chart.js.

The dashboard displays:

* Total processed records
* Regional distribution
* State distribution
* City distribution
* Area-code distribution
* Silver-layer records in tabular format

A lightweight Python HTTP server is used to serve the dashboard and the generated data files locally.

## Technologies

* Python
* Requests
* REST API
* JSON
* CSV
* HTML
* JavaScript
* Chart.js
* Medallion Architecture
* Local Data Lake

## Project structure

```text
viacep-medallion-pipeline/
│
├── datalake/
│   ├── bronze/
│   ├── silver/
│   └── gold/
│
├── extracao_bronze.py
├── processamento_silver.py
├── processamento_gold.py
├── dashboard_server.py
├── index.html
├── requirements.txt
├── .gitignore
└── README.md
```

## Pipeline scripts

| File                      | Responsibility                                                            |
| ------------------------- | ------------------------------------------------------------------------- |
| `extracao_bronze.py`      | Extracts postal code data from the ViaCEP API and stores the raw response |
| `processamento_silver.py` | Cleans, standardizes, enriches and deduplicates the Bronze data           |
| `processamento_gold.py`   | Generates analytical aggregations from the consolidated Silver dataset    |
| `dashboard_server.py`     | Starts the local HTTP server used by the dashboard                        |
| `index.html`              | Displays processed data and Gold-layer metrics                            |

## Requirements

* Python 3.10 or newer
* Internet connection for ViaCEP API requests

## Installation

Clone the repository:

```bash
git clone https://github.com/samufoliveira/viacep-medallion-pipeline.git
cd viacep-medallion-pipeline
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the environment.

### Windows PowerShell

```powershell
venv\Scripts\Activate.ps1
```

### Linux or macOS

```bash
source venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

## Running the pipeline

Execute the scripts in the following order.

### 1. Extract data to Bronze

```bash
python extracao_bronze.py
```

This script requests postal code data from ViaCEP and saves the raw JSON response in the Bronze layer.

### 2. Process the Silver layer

```bash
python processamento_silver.py
```

This script cleans, standardizes and deduplicates the records stored in Bronze.

### 3. Generate Gold metrics

```bash
python processamento_gold.py
```

This script creates aggregated metrics from the consolidated Silver dataset.

### 4. Start the dashboard

```bash
python dashboard_server.py
```

Open the following address in your browser:

```text
http://localhost:8000
```

## Current limitations

* The extraction script currently requests one predefined postal code per execution.
* The pipeline runs locally and does not use distributed processing.
* The scripts must be executed manually and in sequence.
* The project does not currently include automated tests.
* The dashboard is intended for local demonstration.

## Planned improvements

* Read multiple postal codes from a CSV file
* Add command-line parameters for postal code selection
* Add request timeout and retry handling
* Validate malformed or nonexistent postal codes
* Add structured logging
* Add automated tests with Pytest
* Create an orchestrated pipeline
* Store data in Parquet format
* Implement the pipeline with PySpark and Delta Lake
* Deploy the dashboard
* Add CI/CD with GitHub Actions

## Learning objectives

This project was developed to practice and demonstrate:

* Data ingestion from REST APIs
* Separation of raw, processed and analytical data
* Medallion Architecture
* Data quality and standardization
* Data lineage
* Idempotent processing
* Deduplication strategies
* Analytical data aggregation
* End-to-end pipeline organization

## Data source

The project uses the public [ViaCEP](https://viacep.com.br/) API, which provides address information for Brazilian postal codes.

## Author

Developed by **Samuel Fernandes de Oliveira** as part of his Data Engineering portfolio.
