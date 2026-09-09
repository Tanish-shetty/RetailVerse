from functools import lru_cache
import pandas as pd
from sqlalchemy import create_engine, text
from ..core.config import ROOT, settings


@lru_cache
def engine():
    url = settings().database_url
    if not url.startswith('mysql'):
        raise ValueError('Configure a MySQL DATABASE_URL')
    return create_engine(url, pool_pre_ping=True, connect_args={'connect_timeout': 5})


def read_sales(filters: dict | None = None) -> pd.DataFrame:
    filters = {k: v for k, v in (filters or {}).items() if v is not None and v != ''}
    allowed = {'start', 'end', 'region', 'state', 'city', 'category', 'brand', 'product_id', 'promotion_id'}
    if set(filters) - allowed:
        raise ValueError('Unsupported filter')
    if settings().data_source == 'mysql':
        clauses = []
        for key in filters:
            clauses.append(f"date {'>=' if key == 'start' else '<='} :{key}" if key in {'start','end'} else f'{key} = :{key}')
        query = 'SELECT * FROM sales_detail' + (' WHERE ' + ' AND '.join(clauses) if clauses else '')
        with engine().connect() as connection:
            frame = pd.read_sql(text(query), connection, params=filters)
    else:
        frame = pd.read_csv(ROOT / 'data/processed/sales.csv', parse_dates=['date'])
        for key, value in filters.items():
            if key == 'start':
                frame = frame[frame.date >= pd.Timestamp(value)]
            elif key == 'end':
                frame = frame[frame.date <= pd.Timestamp(value)]
            else:
                frame = frame[frame[key] == value]
    frame['date'] = pd.to_datetime(frame.date)
    return frame
