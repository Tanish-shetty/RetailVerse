# RetailIQ

**FMCG Consumer & Sales Intelligence Platform** — a working portfolio application connecting
transaction data to sales analytics, customer segmentation, product health, demand forecasts,
anomaly review and an evidence-based analytics Copilot.

## Overview & business problem
Retail teams need to understand what sold, whether it was profitable, who bought it and what
deserves attention next. RetailIQ brings these questions into a filterable analytical workspace.
No real-world dataset was supplied: the included generator produces a clearly labeled,
reproducible synthetic fixture. Its results are demonstrations, not market claims.

## Features
- Seven React pages: Overview, Consumers, Products, Promotions, Forecasting, Anomalies and Copilot. Overview includes monthly sales performance.
- Audited ETL, profiling notebook, MySQL star schema and SQL analytical examples.
- Revenue/profit/units/AOV/margin, regional/category comparisons and repeat purchase rate.
- Explained RFM rules and silhouette-selected K-Means clusters with actual profiles.
- Chronological recursive forecast evaluation; deploy XGBoost only when it beats the baseline.
- Materiality-gated Isolation Forest alerts and transparent product health components.
- Plotly charts, shared dates/region/category and additional filters, paginated tables and JSON export.
- Read-only analytical operations, optional Groq recommendations and graceful provider failure.

## Architecture & tech stack
Python, Pandas, NumPy → MySQL/SQL → analytics and scikit-learn/XGBoost → FastAPI/Pydantic →
React/TypeScript/Plotly. Groq receives bounded analytical evidence rather than unrestricted
database access. See [architecture](docs/architecture.md) and [schema](docs/database-schema.md).

## Installation & environment variables
Validated environment: Windows, Python 3.13, Node 24, MySQL 8.0.46. Use a recent compatible
Python and Node installation. From the repository root, in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
cd frontend
npm.cmd ci
cd ..
```

The initial development environment was created with `--system-site-packages` to reuse
installed analytics libraries. The clean installation above is the reproducible setup path.
PowerShell may block npm.ps1; `npm.cmd` avoids changing your execution policy.

`.env` supports DATA_SOURCE (`csv` or `mysql`), DATABASE_URL (SELECT-only account),
ETL_DATABASE_URL (loader account), GROQ_API_KEY, GROQ_MODEL and CORS_ORIGINS.
Credentials are never included in the repository. Copy `.env.example` only if `.env`
does not already exist; preserve existing configuration.

## Dataset & data pipeline
```powershell
.\.venv\Scripts\python.exe -m backend.etl.synthetic
.\.venv\Scripts\python.exe -m backend.etl.pipeline data/raw/synthetic_sales.csv
```
The seeded fixture spans 2023–2025 and contains 21,651 lines. Input contract:
[data dictionary](docs/data-dictionary.md). To replace it, place a mapped CSV in `data/raw/`
and pass its path to the same ETL command. Inspect `data/processed/etl-audit.json` and
`profile.json`; invalid input stops ingestion. The EDA notebook is
[notebooks/01_eda.ipynb](notebooks/01_eda.ipynb).

## Database schema & SQL analytics
Create a dedicated `retailiq` MySQL database and configure the two database URLs. Then:
```powershell
.\.venv\Scripts\python.exe -m backend.etl.load_mysql
```
Run `sql/indexes.sql` once using your database client. Set DATA_SOURCE=mysql and restart the
API. `schema.sql` defines dimensions and line-grain facts, `views.sql` joins them, and
`analytics.sql` demonstrates financial KPIs, temporal windows, rankings and customer/campaign
analysis. The loader refuses existing populated facts. CSV mode is explicit; MySQL errors
never silently select another source. See [database setup details](docs/database-schema.md).

## Running locally
In one terminal from the root:
```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```
In another:
```powershell
cd frontend
npm.cmd run dev
```
Open http://localhost:5173. Vite proxies `/api` to FastAPI. The runtime never needs database
credentials in the browser. Production requires an HTTPS reverse proxy, appropriate CORS,
authentication and rate limiting; this repository is configured for local portfolio use.

## API documentation
Interactive OpenAPI documentation: http://127.0.0.1:8000/docs.

| Endpoint | Purpose |
|---|---|
| GET /api/dashboard/overview | Revenue, profit, units, orders, AOV, margin, repeat rate |
| GET /api/sales/trend | Monthly revenue/profit and MoM/YoY |
| GET /api/sales/by-region, /api/sales/by-category | Grouped performance |
| GET /api/products/top, /api/products/performance | Revenue-ranked SKUs and health |
| GET /api/customers/rfm, /api/customers/segments | RFM and evaluated clusters |
| GET /api/promotions/performance | Campaign/discount outcomes |
| GET /api/forecast | Baseline/model metrics and future weekly units |
| GET /api/anomalies | Material sales review candidates |
| GET /api/filters | Available dimension values and date coverage |
| POST /api/copilot/query | `{ "question": "...", "filters": {} }` |

GET analytics accept start/end ISO dates, region, state, city, category, brand, product_id,
promotion_id, limit (1–1000) and offset. List responses include total and source metadata.
No matching records is a successful empty response; invalid inputs return 422; unavailable
data returns 503. Cluster/forecast objects are not paginated.

## Customer segmentation, demand forecasting & anomaly detection
See [ML methodology](docs/ml-methodology.md). Run `python scripts/evaluate.py` to reproduce
[measured evaluation results](docs/evaluation-results.json). Scores and model errors must be
reported with their synthetic provenance. The application may correctly choose the baseline.

## Product Health Score & promotion analytics
[Analytics methodology](docs/analytics-methodology.md) defines every KPI, RFM rule, health
component, weight and classification. Promotion comparisons are descriptive associations,
not causal lift or ROI; campaign costs and treatment assignment are unavailable.

## Groq AI Copilot & example questions
Set a Groq key and model in `.env` to enable generated recommendations; evidence and numerical
summaries work without it. See [Copilot architecture and limits](docs/ai-copilot.md).

- Which region is performing best?
- Compare Maharashtra and Gujarat sales in Q2 2025.
- Which products are declining?
- Who are our most valuable customers?
- What does demand look like next month?
- Are discounts associated with lower margins?

## Frontend & screenshots
The dashboard uses a restrained green palette, responsive navigation, interactive Plotly
charts and clear loading/empty/error states. Filters update the selected page; exports
contain its computed data and provenance. Screenshots should be captured from the running
application after loading the dataset; no fabricated screenshot is supplied.

## Testing
```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts/evaluate.py
.\.venv\Scripts\python.exe -m nbconvert --to notebook --execute --inplace notebooks/01_eda.ipynb
cd frontend
npm.cmd run build
```
Tests cover ETL, metric reconciliation, RFM, health bounds, leakage prevention, forecasts,
constant/spiked anomaly series, endpoints, validation, unsupported/injection requests,
empty selections and mocked Groq failures. MySQL integration tests require configured
credentials and are explicitly skipped otherwise. Provider calls are mocked.

## Future improvements
Real licensed transaction data; returns and inventory; promotion exposure/cost data;
rolling-origin forecast evaluation; calibrated uncertainty; persistent versioned models;
SQL pushdown for large datasets; authentication and rate limits; richer language parsing;
independent validation of generated recommendations.

## Author
Maintained by the repository owner. Add your preferred name and portfolio links before publishing.
