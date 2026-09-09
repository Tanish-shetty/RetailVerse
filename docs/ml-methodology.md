# ML methodology

## Customer clustering
Log1p of recency, frequency and monetary; standard scaling; K-Means with fixed seed 42 and
10 initializations. Evaluate k=2 through min(6, n−1, number of unique feature rows), requiring
at least ten customers. Select the largest silhouette score, report inertia and mean RFM
profiles. IDs are arbitrary; no fabricated persona names. Silhouette is internal separation,
not accuracy. Uniform synthetic customers are not a benchmark for actual segmentation.

## Forecasting
Aggregate to W-SUN weeks, excluding partial first/last weeks. Features are prior 1/2/4/8
weeks, a strictly shifted four-week mean, month and ISO week. Require at least 40 feature
rows after lag creation (48 complete weeks). Hold out min(12, n/4) final weeks chronologically.
Both models forecast the entire holdout recursively, using their own predicted lags, not
held-out observations. Compare a four-week moving average against XGBoost (120 trees,
depth 3, learning rate .04). Report MAE, RMSE and MAPE excluding zero actuals. MAPE may
be undefined for all-zero targets. XGBoost is selected only for at least 2% lower holdout
MAE. Refit the selected approach on all observed data and recursively predict four weeks.

No uncertainty interval is fabricated. Current evaluation uses one holdout and model
selection on it, so it is a validation estimate, not an independent final test estimate.
Rolling-origin backtesting and a separate final test set are future improvements. Weekly
forecasts are not full calendar-month forecasts. Filter by product/category to change scope.

## Anomalies
For each product and region, weekly revenue is compared to the prior eight-week median
and standard deviation (floor INR 1). Isolation Forest fits standardized residuals using
seed 42 and automatic contamination. At least 20 residual observations are required.
Flag only if the model decision is negative, absolute standardized deviation ≥3, and
absolute revenue change ≥25% of the expected value. Severity is High at ≥5 deviations,
otherwise Medium. Score = negative decision function; higher means more unusual.

This is retrospective, unsupervised inspection with no ground-truth precision/recall.
Confirm alerts against invoices, stock-outs, campaign calendars and ETL incidents. Partial
boundary weeks are excluded. The model's fit includes the inspected period; it is not a
prospective online detector. Product/region alerts may describe the same underlying sales.

Run `python scripts/evaluate.py` for actual results in `docs/evaluation-results.json`.
