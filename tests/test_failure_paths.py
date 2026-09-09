from types import SimpleNamespace
import pandas as pd
import pytest
from backend.app.services import copilot
from backend.app.ml.segmentation import segment
from backend.app.ml.anomalies import anomalies
from backend.etl.pipeline import clean
from backend.etl.synthetic import generate


@pytest.mark.parametrize('mode',['failure','malformed','invented_number','valid'])
def test_groq_failure_and_output_validation(monkeypatch,mode):
    monkeypatch.setattr(copilot,'settings',lambda:SimpleNamespace(groq_api_key='test-only',groq_model='test'))
    def create(**kwargs):
        if mode=='failure':
            raise TimeoutError('private provider message')
        output={'malformed':'not json','invented_number':'{"recommendation":"Increase sales by 99 percent"}',
                'valid':'{"recommendation":"Review the regional mix before changing promotion strategy."}'}[mode]
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=output))])
    monkeypatch.setattr(copilot,'Groq',lambda **kwargs:SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create))))
    result = copilot.query('Which region is performing best?',{})
    assert result['key_metrics']['revenue'] > 0
    assert result['mode'] == ('groq-assisted' if mode=='valid' else 'deterministic')
    assert 'private provider message' not in str(result)


def test_empty_copilot():
    result=copilot.query('Show sales trends',{'region':'not-a-region'})
    assert result['supporting_evidence']==[]


def test_detect_large_spike():
    frame=pd.DataFrame({'date':pd.date_range('2024-01-01',periods=700),'revenue':100.,'product_name':'A','region':'West'})
    frame.loc[500:506,'revenue']=10000
    result=anomalies(frame)
    assert any(row['severity']=='High' and row['direction']=='spike' for row in result)


def test_missing_schema_and_conflicting_ids():
    with pytest.raises(ValueError,match='Missing required'):
        clean(pd.DataFrame({'date':[]}))
    frame=generate().head(5)
    frame.loc[1,'line_id']=frame.loc[0,'line_id']
    with pytest.raises(ValueError,match='Conflicting'):
        clean(frame)


def test_segmentation_requires_customers():
    frame=clean(generate().head(2))[0]
    assert segment(frame)['status']=='insufficient_data'
