"""Produce measured model and KPI results for the current processed snapshot."""
import json
import sys
from pathlib import Path
root = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
from backend.app.db.repository import read_sales
from backend.app.services.analytics import analyze
frame = read_sales()
report = {'provenance':frame.source.unique().tolist(),'rows':len(frame),'overview':analyze(frame,'overview')}
for name in ['segments','forecast','anomalies']:
    result = analyze(frame,name)
    if name == 'segments':
        result.pop('customers',None)
    if name == 'forecast':
        result.pop('history',None)
    report[name]=result
(root/'docs/evaluation-results.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'rows':len(frame),'segmentation_k':report['segments'].get('selected_k'),
    'silhouette':report['segments'].get('silhouette'), 'forecast_model':report['forecast'].get('selected_model'),
    'baseline':report['forecast'].get('baseline_metrics'),'xgboost':report['forecast'].get('xgboost_metrics'),
    'anomalies':len(report['anomalies'])},indent=2))
