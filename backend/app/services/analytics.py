import json
import pandas as pd
from ..analytics import sales, customers, products, promotions
from ..ml.segmentation import segment
from ..ml.forecast import forecast
from ..ml.anomalies import anomalies


def records(value):
    if isinstance(value, pd.DataFrame):
        return json.loads(value.to_json(orient='records',date_format='iso'))
    return value


OPERATIONS = {
    'overview': sales.overview, 'trend': sales.trend,
    'regions': lambda frame: sales.aggregate(frame,'region'),
    'categories': lambda frame: sales.aggregate(frame,'category'),
    'products': products.performance, 'rfm': customers.rfm,
    'segments': segment, 'promotions': promotions.performance,
    'forecast': forecast, 'anomalies': anomalies,
}


def analyze(frame: pd.DataFrame, operation: str):
    if operation not in OPERATIONS:
        raise ValueError('Unsupported analytical operation')
    return records(OPERATIONS[operation](frame))
