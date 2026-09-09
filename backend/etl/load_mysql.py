"""Load a validated snapshot transactionally; refuses to overwrite populated tables."""
import pandas as pd
from sqlalchemy import create_engine, text
from backend.app.core.config import ROOT, settings
from .pipeline import clean


def load() -> None:
    config = settings()
    if not config.etl_database_url.startswith('mysql'):
        raise ValueError('Set ETL_DATABASE_URL to the dedicated loader account')
    frame, _ = clean(pd.read_csv(ROOT / 'data/processed/sales.csv'))
    engine = create_engine(config.etl_database_url)
    with engine.begin() as conn:
        for filename in ['schema.sql', 'views.sql']:
            sql = (ROOT / 'sql' / filename).read_text()
            for statement in sql.split(';'):
                if statement.strip():
                    conn.execute(text(statement))
    with engine.begin() as conn:
        if conn.scalar(text('SELECT COUNT(*) FROM fact_sales')):
            raise ValueError('Database already populated; use a new dedicated database for a new snapshot')
        dims = {'dim_customer': ['customer_id'], 'dim_product': ['product_id','product_name','brand','category'],
                'dim_location': ['location_id','store','city','state','region'],
                'dim_promotion': ['promotion_id','campaign']}
        for table, columns in dims.items():
            frame[columns].drop_duplicates().to_sql(table, conn, if_exists='append', index=False, chunksize=1000)
        dates = pd.DataFrame({'date': pd.date_range(frame.date.min(), frame.date.max())})
        dates['date_id'] = dates.date.dt.strftime('%Y%m%d').astype(int)
        for col in ['day','month','quarter','year']:
            dates[col] = getattr(dates.date.dt, col)
        dates['week'] = dates.date.dt.isocalendar().week.astype(int)
        dates.to_sql('dim_date', conn, if_exists='append', index=False)
        frame['date_id'] = frame.date.dt.strftime('%Y%m%d').astype(int)
        columns = ['line_id','transaction_id','date_id','customer_id','product_id','location_id',
                   'promotion_id','quantity','unit_price','unit_cost','discount','revenue','cost','profit','source']
        frame[columns].to_sql('fact_sales', conn, if_exists='append', index=False, chunksize=1000)
    print('MySQL snapshot loaded successfully')


if __name__ == '__main__':
    load()
