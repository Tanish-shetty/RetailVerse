# Data dictionary

Grain: one SKU line within an order. Currency: INR. Dates: local business calendar dates,
without time-of-day or timezone conversion. All fields below are required, non-null.

| Field | Type | Meaning / validation |
|---|---|---|
| line_id | string | Globally unique line key; conflicting duplicates rejected |
| transaction_id | string | Order key; shared lines must agree on customer, date, location |
| date | ISO date | Business sale date, YYYY-MM-DD |
| customer_id | string | Pseudonymous customer key; no demographics are inferred |
| product_id | string | SKU key |
| product_name, brand, category | string | Stable product attributes; map changes before ingestion |
| location_id, store | string | Retail location key and display name |
| city, state, region | string | Location attributes; whitespace and casing normalized |
| promotion_id, campaign | string | Campaign key/name; use an explicit no-promotion key |
| quantity | integer | Positive units; returns need a separate model |
| unit_price | decimal | Non-negative undiscounted price per unit in INR |
| unit_cost | decimal | Non-negative product cost per unit in INR |
| discount | decimal | Fraction from 0 to 1; 0.10 means 10% |
| source | string | Provenance, e.g. synthetic or an identified licensed source |
| revenue | derived decimal | Round(quantity × unit_price × (1 − discount), 2) |
| cost | derived decimal | Round(quantity × unit_cost, 2) |
| profit | derived decimal | revenue − cost; gross product profit only |

If derived fields are supplied, ETL reconciles them within one paisa. Negative profit is
valid; negative price or quantity is not. Exact duplicates are logged and removed. No
missing cost, customer, or date is imputed. IQR outliers are profiled, not automatically removed.
