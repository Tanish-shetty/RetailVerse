# Analytics methodology

Revenue is net of line discounts. Cost is quantity × historical unit cost. Profit is gross
product profit, excluding unavailable tax, logistics and operating expenses. Orders count
distinct transaction IDs. AOV = revenue / orders. Margin = profit / revenue, not the average
of line margins. Repeat purchase rate = customers with >1 distinct order / active customers.
KPIs return zero on an empty selection; charts return no records. Missing growth is null.

Monthly trends sum complete and partial calendar months as observed, filling internal
zero-sale months. MoM and YoY compare against 1 and 12 calendar months ago; denominators
of zero are undefined, serialized as null. Filter boundaries may produce partial periods.
Use full calendar months for fair growth comparisons.

RFM reference date is the latest selected transaction + one day. Frequency counts orders,
monetary sums revenue. Scores are ceil(5 × average percentile rank), with recency reversed.
Ties receive equal scores; small/equal groups may not occupy all five bins. Rules apply in
order: Champions R/F/M≥4; Lost R≤1; At Risk R≤2 and F≥3; New R≥4 and one order; Loyal R≥3
and F≥3; remainder Potential Loyalists. These relative labels are heuristics, not churn labels.

## Product health

Score = 100 × (0.25 growth + 0.30 margin + 0.15 volume + 0.15 demand + 0.15 consistency).
Growth compares two adjacent 90-day windows ending on the latest selected date, requires
180 calendar days of coverage, clips growth to [-50%,50%] and maps it to [0,1]. Missing growth
is neutral 0.5. Margin clips margin/40% to [0,1]. Volume is the within-selection percentile
rank of units; demand is the percentile rank of distinct customers. Consistency is
1/(1+monthly coefficient of variation), including zero-sale internal months. Scores are
relative to selected peers and are not comparable across different filters without care.

Margin receives the highest weight to favor profitable demand. Growth follows because
direction matters; remaining factors balance scale, reach and stability. Weights are a
documented business heuristic, not learned or validated ground truth. Classification order:
score<35 At Risk; growth<−10% Declining; growth>15% and score≥65 High Growth; score≥65
Healthy; otherwise Stable. Exposed components enable auditing and sensitivity analysis.

Promotion summaries show revenue, profit, margin and units per line at each campaign/
discount. Discount revenue share highlights dependency but does not estimate incremental
lift. Product mix, seasonality, exposure and customer selection are confounders. Use an
experiment or defensible quasi-experimental design before claiming causal effectiveness.
