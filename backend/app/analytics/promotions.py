import pandas as pd


def performance(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.groupby(['campaign','discount']).agg(lines=('line_id','count'), units=('quantity','sum'),
        revenue=('revenue','sum'), profit=('profit','sum'), units_per_line=('quantity','mean')).reset_index()
    result['margin_pct'] = 100*result.profit/result.revenue.where(result.revenue != 0)
    return result
