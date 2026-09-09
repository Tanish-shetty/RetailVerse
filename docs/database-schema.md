# Database schema

MySQL 8.0.16+ enforces checks. `fact_sales` has one row per line, not order. The order ID
is deliberately non-unique. Dimensions contain only supported source attributes; no fake
age/gender fields are added. Location includes retailer/store, and unit cost/discount stay
on the fact because they may change transaction by transaction.

| Table | Primary key | Contents |
|---|---|---|
| fact_sales | line_id | Order ID, all dimension keys, financial measures, provenance |
| dim_customer | customer_id | Pseudonymous customer identity |
| dim_product | product_id | Name, brand, category |
| dim_location | location_id | Store, city, state, region |
| dim_promotion | promotion_id | Campaign name |
| dim_date | date_id (YYYYMMDD) | Continuous date spine, day, ISO week, month, quarter, year |

All fact dimension references have foreign keys. Money uses DECIMAL, not FLOAT. Pandas
calculations round line measures before summing. `sales_detail` is a joined read-only
analytical view. Indexes cover date/product, location/date and customer/order. Run
`sql/indexes.sql` once after the first load; repeated CREATE INDEX statements are not
idempotent. The snapshot loader refuses a populated fact table and never truncates it.
DDL is initialized separately from the atomic dimension/fact insertion transaction.

Create a dedicated database and accounts with your MySQL administrator. The loader needs
CREATE, CREATE VIEW, SELECT, INSERT and INDEX for initialization. The runtime account only
needs SELECT on retailiq tables/views. Never use root as the application account. Supply
URL-encoded credentials through `.env`, not source files. This project does not alter the
existing MySQL server or its users automatically.

`sql/analytics.sql` demonstrates joins, aggregations, CTEs, ranking and lag windows.
Global monthly growth uses the date spine; regional/product SQL examples explicitly
compare previous observed months and can span gaps. Python product growth instead uses
two equal 90-day periods. These are distinct metrics and should not be conflated.
