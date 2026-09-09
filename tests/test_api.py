from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app,raise_server_exceptions=False)


def test_endpoints():
    for path in ['dashboard/overview','sales/trend','sales/by-region','products/performance','customers/rfm','promotions/performance','customers/segments','forecast','anomalies']:
        response = client.get('/api/'+path)
        assert response.status_code == 200, response.text
        assert 'data' in response.json()


def test_validation_and_empty():
    assert client.get('/api/sales/trend?start=bad').status_code == 422
    assert client.get('/api/sales/trend?start=2025-01-01&end=2024-01-01').status_code == 422
    assert client.get('/api/sales/trend?limit=-1').status_code == 422
    assert client.get('/api/sales/trend?region=Unknown').json()['rows'] == 0
    assert client.post('/api/copilot/query',json={'question':''}).status_code == 422


def test_copilot():
    result = client.post('/api/copilot/query',json={'question':'Compare Maharashtra and Gujarat sales in Q2 2025'}).json()
    assert {row['state'] for row in result['supporting_evidence']} == {'Maharashtra','Gujarat'}
    unsafe = client.post('/api/copilot/query',json={'question':'DROP TABLE sales'}).json()
    assert unsafe['supporting_evidence'] == []


def test_missing_database(monkeypatch):
    from backend.app.api import routes
    def fail(*args,**kwargs):
        raise ConnectionError('secret password')
    monkeypatch.setattr(routes,'read_sales',fail)
    response = client.get('/api/dashboard/overview')
    assert response.status_code == 503
    assert 'secret' not in response.text
