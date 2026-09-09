"""Strict, audited transaction ingestion and profiling."""
import argparse
import json
import logging
from pathlib import Path
import numpy as np
import pandas as pd
from .synthetic import ROOT

REQUIRED = ['line_id', 'transaction_id', 'date', 'customer_id', 'product_id',
            'product_name', 'brand', 'category', 'location_id', 'store', 'city',
            'state', 'region', 'promotion_id', 'campaign', 'quantity', 'unit_price',
            'unit_cost', 'discount', 'source']
NUMERIC = ['quantity', 'unit_price', 'unit_cost', 'discount']


def clean(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    missing = set(REQUIRED) - set(raw.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    frame = raw.copy()
    duplicates = int(frame.duplicated().sum())
    frame = frame.drop_duplicates()
    for col in set(REQUIRED) - set(NUMERIC) - {'date'}:
        frame[col] = frame[col].astype('string').str.strip()
        if frame[col].isna().any() or frame[col].eq('').any():
            raise ValueError(f"Missing value in {col}; correct source before loading")
    for col in ['region', 'state', 'city', 'category']:
        frame[col] = frame[col].str.replace(r'\s+', ' ', regex=True).str.title()
    frame['source'] = frame.source.str.lower()
    frame['date'] = pd.to_datetime(frame.date, format='%Y-%m-%d', errors='coerce')
    for col in NUMERIC:
        frame[col] = pd.to_numeric(frame[col], errors='coerce')
    invalid = (frame.date.isna() | ~np.isfinite(frame[NUMERIC]).all(axis=1)
               | (frame.quantity <= 0) | (frame.quantity % 1 != 0)
               | (frame.unit_price < 0) | (frame.unit_cost < 0)
               | ~frame.discount.between(0, 1))
    if invalid.any():
        raise ValueError(f"{int(invalid.sum())} invalid rows; no output written. Example lines: {frame.loc[invalid, 'line_id'].head().tolist()}")
    if frame.line_id.duplicated().any():
        raise ValueError('Conflicting duplicate line IDs')
    for key, attrs in [('transaction_id', ['date', 'customer_id', 'location_id']),
                       ('product_id', ['product_name', 'brand', 'category']),
                       ('location_id', ['store', 'city', 'state', 'region']),
                       ('promotion_id', ['campaign'])]:
        if (frame.groupby(key)[attrs].nunique() > 1).any().any():
            raise ValueError(f'Inconsistent attributes for {key}')
    revenue = (frame.quantity * frame.unit_price * (1-frame.discount)).round(2)
    cost = (frame.quantity * frame.unit_cost).round(2)
    for col, expected in [('revenue', revenue), ('cost', cost), ('profit', revenue-cost)]:
        if col in frame and not np.allclose(pd.to_numeric(frame[col], errors='coerce'), expected, atol=.011):
            raise ValueError(f'Inconsistent provided {col}')
        frame[col] = expected.round(2)
    return frame, {'input_rows': len(raw), 'output_rows': len(frame), 'exact_duplicates_removed': duplicates,
                   'rejected_rows': 0, 'source': frame.source.unique().tolist()}


def profile(frame: pd.DataFrame) -> dict:
    numerical = frame.select_dtypes('number')
    q1, q3 = numerical.quantile(.25), numerical.quantile(.75)
    return {'rows': len(frame), 'columns': len(frame.columns),
            'types': frame.dtypes.astype(str).to_dict(), 'missing': frame.isna().sum().to_dict(),
            'duplicates': int(frame.duplicated().sum()), 'unique': frame.nunique().to_dict(),
            'date_start': str(frame.date.min()), 'date_end': str(frame.date.max()),
            'numerical': numerical.describe().to_dict(),
            'iqr_outliers': ((numerical < q1-1.5*(q3-q1)) | (numerical > q3+1.5*(q3-q1))).sum().to_dict(),
            'distributions': {c: frame[c].value_counts().head(20).to_dict() for c in ['category', 'region', 'product_name', 'customer_id']}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=Path)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    raw = pd.read_csv(args.path, dtype={c: 'string' for c in REQUIRED if c not in NUMERIC})
    frame, audit = clean(raw)
    target = ROOT / 'data/processed'
    target.mkdir(exist_ok=True, parents=True)
    frame.to_csv(target / 'sales.csv', index=False)
    (target / 'etl-audit.json').write_text(json.dumps(audit, indent=2), encoding='utf-8')
    (target / 'profile.json').write_text(json.dumps(profile(frame), indent=2, default=str), encoding='utf-8')
    logging.info('ETL complete: %s', audit)
