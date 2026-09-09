# Implementation plan and discovery

The repository initially contained only .git. Windows, Python 3.13.0, Node 24.11.1,
npm 11.6.2, MySQL 8.0.46 (running) are available. No dataset or database credentials
were supplied. Docker is installed but its daemon is unavailable. Use npm.cmd on Windows.

1. Establish a deterministic synthetic dataset, dictionary, profiling notebook and audited ETL.
2. Define MySQL dimensions, fact grain, constraints, views, indexes and SQL analytics.
3. Add reusable analytics, RFM, evaluated clustering, chronological forecasting and anomalies.
4. Add validated FastAPI services and controlled evidence-based Groq operations.
5. Build the React/TypeScript/Plotly interface with shared filters and explicit errors.
6. Validate calculations, failure paths, API, notebook and frontend build; document operation.

MySQL is the primary production store. An explicit CSV development mode allows this
project to run before credentials are configured. It never silently falls back from MySQL.
