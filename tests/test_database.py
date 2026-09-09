"""Live MySQL integration test, enabled only against the configured project database."""
import pytest
from sqlalchemy import create_engine, text
from backend.app.core.config import settings, ROOT


@pytest.mark.skipif(not settings().database_url,reason='MySQL credentials not configured')
def test_mysql_analytics():
    engine=create_engine(settings().database_url)
    with engine.connect() as conn:
        kpis=conn.execute(text('SELECT SUM(revenue), SUM(cost), SUM(profit) FROM fact_sales')).one()
        assert float(kpis[0])-float(kpis[1]) == pytest.approx(float(kpis[2]))
        queries=(ROOT/'sql/analytics.sql').read_text().split(';')
        for query in queries:
            if query.strip():
                conn.execute(text(query)).fetchall()
