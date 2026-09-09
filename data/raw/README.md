# Input contract

Place transaction-line CSV files here. Run `python -m backend.etl.pipeline path/to/file.csv`.
Required columns are documented in `docs/data-dictionary.md`. A transaction ID is an order;
a line ID uniquely identifies one SKU line in that order. Amounts use INR, discount is a
fraction in [0, 1]. Dates must be ISO calendar dates. Returns are not supported: ingest them
through a separate returns model rather than silently treating negative quantities as sales.

No real data was supplied. `python -m backend.etl.synthetic` creates a deterministic,
explicitly synthetic 36-month fixture. Its findings are demonstrations, not market evidence.
Do not combine sources or currencies without an explicit mapping and currency conversion.
