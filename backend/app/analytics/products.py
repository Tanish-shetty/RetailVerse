import numpy as np
import pandas as pd
from .sales import aggregate


def performance(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame()
    result = aggregate(frame, 'product_id').set_index('product_id')
    result = result.join(frame.groupby('product_id')[['product_name','category','brand']].first())
    monthly = frame.pivot_table(index=pd.Grouper(key='date', freq='MS'), columns='product_id', values='revenue', aggfunc='sum', fill_value=0)
    monthly = monthly.reindex(pd.date_range(frame.date.min().to_period('M').start_time, frame.date.max().to_period('M').start_time, freq='MS'), fill_value=0)
    # Compare equal 90-day periods ending at the filter end; not unmatched calendar fragments.
    end = frame.date.max()
    current = frame[frame.date > end-pd.Timedelta(days=90)].groupby('product_id').revenue.sum()
    prior = frame[(frame.date <= end-pd.Timedelta(days=90)) & (frame.date > end-pd.Timedelta(days=180))].groupby('product_id').revenue.sum()
    result['growth_pct'] = (current.reindex(result.index, fill_value=0)/prior.reindex(result.index).replace(0,np.nan)-1)*100
    if (end-frame.date.min()).days < 179:
        result['growth_pct'] = np.nan
    consistency = 1/(1+monthly.std(ddof=0)/monthly.mean().replace(0,np.nan))
    demand = frame.groupby('product_id').customer_id.nunique()
    result['growth_component'] = ((result.growth_pct.clip(-50,50)+50)/100).fillna(.5)
    result['margin_component'] = (result.margin_pct/40).clip(0,1).fillna(0)
    result['volume_component'] = result.units.rank(pct=True)
    result['demand_component'] = demand.rank(pct=True)
    result['consistency_component'] = consistency.fillna(0)
    result['health_score'] = 100*(.25*result.growth_component+.30*result.margin_component+
        .15*result.volume_component+.15*result.demand_component+.15*result.consistency_component)
    result['health'] = np.select([result.health_score < 35, result.growth_pct < -10,
        (result.growth_pct > 15) & (result.health_score >= 65), result.health_score >= 65],
        ['At Risk','Declining','High Growth','Healthy'], default='Stable')
    result['discount_revenue_share_pct'] = frame[frame.discount > 0].groupby('product_id').revenue.sum().reindex(result.index,fill_value=0)/result.revenue.replace(0,np.nan)*100
    return result.reset_index()
