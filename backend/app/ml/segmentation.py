import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
from ..analytics.customers import rfm


def segment(frame: pd.DataFrame) -> dict:
    customers = rfm(frame)
    if len(customers) < 10:
        return {'status': 'insufficient_data', 'profiles': [], 'customers': [], 'evaluation': []}
    features = StandardScaler().fit_transform(np.log1p(customers[['recency','frequency','monetary']]))
    unique = len(np.unique(features, axis=0))
    evaluations, candidates = [], []
    for k in range(2, min(6, len(customers)-1, unique)+1):
        model = KMeans(n_clusters=k, random_state=42, n_init=10).fit(features)
        if len(set(model.labels_)) < 2:
            continue
        score = silhouette_score(features, model.labels_, sample_size=min(2000,len(features)), random_state=42)
        evaluations.append({'k': k, 'silhouette': float(score), 'inertia': float(model.inertia_)})
        candidates.append((score, model))
    if not candidates:
        return {'status': 'insufficient_variation', 'profiles': [], 'customers': [], 'evaluation': []}
    score, model = max(candidates, key=lambda pair: pair[0])
    customers['cluster'] = model.labels_
    profiles = customers.groupby('cluster').agg(customers=('customer_id','count'),
        recency=('recency','mean'), frequency=('frequency','mean'), monetary=('monetary','mean')).reset_index()
    return {'status': 'ok', 'selected_k': model.n_clusters, 'silhouette': float(score),
            'evaluation': evaluations, 'profiles': profiles.to_dict('records'),
            'customers': customers.to_dict('records'), 'caveat': 'Exploratory unsupervised clusters; IDs are not business labels.'}
