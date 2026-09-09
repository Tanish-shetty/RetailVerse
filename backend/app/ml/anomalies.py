import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest


def anomalies(frame: pd.DataFrame) -> list[dict]:
    results = []
    for dimension in ['product_name','region']:
        for entity, group in frame.groupby(dimension):
            series = group.set_index('date').revenue.resample('W-SUN').sum()
            series = series[(series.index-pd.Timedelta(days=6) >= frame.date.min()) & (series.index <= frame.date.max())]
            expected = series.shift(1).rolling(8,min_periods=8).median()
            scale = series.shift(1).rolling(8,min_periods=8).std().clip(lower=1)
            data = pd.DataFrame({'observed': series,'expected': expected,'z': (series-expected)/scale}).dropna()
            if len(data) < 20:
                continue
            model = IsolationForest(contamination='auto',random_state=42,n_estimators=100,n_jobs=1).fit(data[['z']])
            data['score'] = -model.decision_function(data[['z']])
            selected = data[(data.score > 0) & (data.z.abs() >= 3) & ((data.observed-data.expected).abs() >= data.expected.abs()*.25)]
            for date,row in selected.iterrows():
                results.append({'entity': entity,'dimension': dimension,'date': str(date.date()),
                    'observed': float(row.observed),'expected': float(row.expected),'anomaly_score': float(row.score),
                    'severity': 'High' if abs(row.z) >= 5 else 'Medium', 'direction': 'spike' if row.z > 0 else 'drop'})
    return sorted(results,key=lambda item:item['anomaly_score'],reverse=True)
