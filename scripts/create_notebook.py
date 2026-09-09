"""Build the EDA notebook with executable business analysis cells."""
from pathlib import Path
import nbformat as nbf

root=Path(__file__).resolve().parents[1]
notebook=nbf.v4.new_notebook()
notebook.cells=[
nbf.v4.new_markdown_cell('''# RetailIQ · Dataset exploration

**Provenance: synthetic demonstration only.** No dataset was supplied. This notebook examines the reproducible fixture and establishes checks to repeat when actual transaction data is supplied. It does not describe a real FMCG market.

Questions: Is the line grain consistent? Does revenue translate into margin? Are customer and seasonal patterns sufficient to justify segmentation and forecasting?'''),
nbf.v4.new_code_cell('''from pathlib import Path
import sys, json
import pandas as pd
import matplotlib.pyplot as plt
root = Path.cwd() if (Path.cwd() / 'backend').exists() else Path.cwd().parent
sys.path.insert(0, str(root))
from backend.etl.pipeline import clean, profile
from backend.app.analytics.sales import overview, trend, aggregate
from backend.app.analytics.customers import rfm
raw = pd.read_csv(root / 'data/raw/synthetic_sales.csv')
sales, audit = clean(raw)
audit'''),
nbf.v4.new_markdown_cell('''## Grain and data quality

Each row is a transaction line. Multiple lines can belong to one order, so counting rows would overstate purchase frequency and understate average order value. Missing costs cannot be imputed as zero because that would inflate profit. Invalid records block ingestion rather than disappearing silently.'''),
nbf.v4.new_code_cell('''report = profile(sales)
display(pd.DataFrame({'dtype':sales.dtypes.astype(str), 'missing':sales.isna().sum(), 'unique':sales.nunique()}))
print('Rows:', len(sales), 'Columns:', len(sales.columns), 'Exact duplicates:', raw.duplicated().sum())
print('Date coverage:', sales.date.min(), 'to', sales.date.max())
display(sales.select_dtypes('number').describe().T)
display(pd.Series(report['iqr_outliers'], name='IQR outliers'))'''),
nbf.v4.new_markdown_cell('''## Revenue, profit and regional mix

Gross profit is discounted revenue minus product cost; shipping, tax, labor and overhead are unavailable. It is not operating profit. Compare margins alongside revenue to avoid recommending high-volume but unprofitable activity.'''),
nbf.v4.new_code_cell('''display(pd.Series(overview(sales)))
display(aggregate(sales,'region'))
display(aggregate(sales,'product_name'))
display(aggregate(sales,'category'))
sales[['revenue','profit']].hist(bins=35, figsize=(10,3))
plt.tight_layout(); plt.show()
monthly = trend(sales)
monthly.plot(x='date', y=['revenue','profit'], figsize=(10,3), ylabel='INR', title='Synthetic monthly financial performance')
plt.tight_layout(); plt.show()
leader = aggregate(sales,'region').iloc[0]
print(f"Observed fixture leader: {leader['region']}, revenue INR {leader['revenue']:,.2f}. This is a generated sample outcome.")'''),
nbf.v4.new_markdown_cell('''## Customer distribution and segmentation suitability

The generator samples customers approximately uniformly. Real retail data often have stronger purchase concentration and inactivity. Consequently synthetic cluster quality must not be presented as evidence that segmentation will generalize to real customers. RFM labels are relative to this observation window, not proof of churn.'''),
nbf.v4.new_code_cell('''customers = rfm(sales)
display(customers.head(10))
display(customers.segment.value_counts())
customers[['recency','frequency','monetary']].hist(bins=25,figsize=(12,3))
plt.tight_layout(); plt.show()
top_share = customers.head(max(1,len(customers)//10)).monetary.sum()/customers.monetary.sum()
print(f'Top customer decile share of revenue: {top_share:.1%}')'''),
nbf.v4.new_markdown_cell('''## Promotions and next analytical steps

Discount assignment and product prices are generated. Units per line comparisons are descriptive, not causal lift. Evaluate forecasting chronologically against a moving-average baseline. Inspect anomaly candidates against the raw transactions and data-quality checks; no confirmed anomaly labels exist.'''),
nbf.v4.new_code_cell('''from backend.app.analytics.promotions import performance
display(performance(sales))
coverage = sales.groupby('product_name').agg(first=('date','min'),last=('date','max'),lines=('line_id','count'))
display(coverage)
print('Review partial boundary months before interpreting MoM/YoY; use full weeks for forecasting.')''')]
notebook.metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.13'}}
(root/'notebooks').mkdir(exist_ok=True)
nbf.write(notebook,root/'notebooks/01_eda.ipynb')
print('Notebook created')
