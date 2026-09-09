import pandas as pd


def overview(frame: pd.DataFrame) -> dict:
    revenue, profit = float(frame.revenue.sum()), float(frame.profit.sum())
    orders = int(frame.transaction_id.nunique())
    customers = frame.groupby('customer_id').transaction_id.nunique()
    return dict(revenue=revenue, profit=profit, units=int(frame.quantity.sum()), orders=orders,
                customers=len(customers), average_order_value=revenue/orders if orders else 0,
                margin_pct=100*profit/revenue if revenue else 0,
                repeat_purchase_pct=100*float((customers > 1).mean()) if len(customers) else 0)


def trend(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame()
    monthly = frame.set_index('date')[['revenue','profit','quantity']].resample('MS').sum()
    monthly['mom_pct'] = monthly.revenue.pct_change(fill_method=None)*100
    monthly['yoy_pct'] = monthly.revenue.pct_change(12, fill_method=None)*100
    return monthly.reset_index()


def aggregate(frame: pd.DataFrame, by: str) -> pd.DataFrame:
    result = frame.groupby(by).agg(revenue=('revenue','sum'), profit=('profit','sum'),
        units=('quantity','sum'), orders=('transaction_id','nunique')).reset_index()
    result['margin_pct'] = result.profit.div(result.revenue.where(result.revenue != 0))*100
    return result.sort_values('revenue', ascending=False)


def monthly_comparison(frame: pd.DataFrame) -> dict:
    """Attribute a monthly revenue difference arithmetically, without claiming causality."""
    if frame.empty:
        return {}
    month = frame.date.max().to_period('M')
    current = frame[frame.date.dt.to_period('M') == month]
    previous = frame[frame.date.dt.to_period('M') == month-1]
    current_revenue = float(current.revenue.sum())
    previous_revenue = float(previous.revenue.sum())
    result = {'month':str(month),'previous_month':str(month-1),'revenue':current_revenue,
              'previous_revenue':previous_revenue if len(previous) else None,
              'change_pct':100*(current_revenue/previous_revenue-1) if previous_revenue else None,
              'regional_changes':[], 'category_changes':[]}
    if previous.empty:
        return result
    for dimension, key in [('region','regional_changes'),('category','category_changes')]:
        combined = pd.concat([current.groupby(dimension).revenue.sum().rename('revenue'),
                              previous.groupby(dimension).revenue.sum().rename('previous_revenue')],axis=1).fillna(0)
        combined['revenue_change'] = combined.revenue-combined.previous_revenue
        result[key] = combined.sort_values('revenue_change').reset_index().to_dict('records')
    return result
