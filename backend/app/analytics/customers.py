import numpy as np
import pandas as pd


def rfm(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame()
    result = frame.groupby('customer_id').agg(last_purchase=('date','max'),
        frequency=('transaction_id','nunique'), monetary=('revenue','sum'))
    result['recency'] = ((frame.date.max()+pd.Timedelta(days=1))-result.last_purchase).dt.days
    for column, label, ascending in [('recency','r_score',False), ('frequency','f_score',True), ('monetary','m_score',True)]:
        result[label] = np.ceil(result[column].rank(pct=True, method='average', ascending=ascending)*5).clip(1,5).astype(int)
    r, f, m = result.r_score, result.f_score, result.m_score
    result['segment'] = np.select([
        (r >= 4) & (f >= 4) & (m >= 4), (r <= 1), (r <= 2) & (f >= 3),
        (r >= 4) & (result.frequency == 1), (r >= 3) & (f >= 3)],
        ['Champions','Lost Customers','At Risk','New Customers','Loyal Customers'], default='Potential Loyalists')
    return result.drop(columns='last_purchase').reset_index().sort_values('monetary', ascending=False)
