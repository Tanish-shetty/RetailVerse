import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor


def features(series: pd.Series) -> pd.DataFrame:
    result = pd.DataFrame({'y': series})
    for lag in [1,2,4,8]:
        result[f'lag_{lag}'] = series.shift(lag)
    result['rolling_4'] = series.shift(1).rolling(4).mean()
    result['month'] = series.index.month
    result['week'] = series.index.isocalendar().week.to_numpy()
    return result.dropna()


def metrics(actual, predicted) -> dict:
    actual, predicted = np.asarray(actual), np.asarray(predicted)
    nonzero = actual != 0
    return {'mae': float(mean_absolute_error(actual,predicted)),
            'rmse': float(np.sqrt(mean_squared_error(actual,predicted))),
            'mape_pct': float(np.mean(np.abs((actual[nonzero]-predicted[nonzero])/actual[nonzero]))*100) if nonzero.any() else None}


def forecast(frame: pd.DataFrame, horizon: int = 4) -> dict:
    if frame.empty:
        return {'status': 'insufficient_data', 'future': [], 'history': []}
    series = frame.set_index('date').quantity.resample('W-SUN').sum().astype(float)
    # Exclude partial first/last weeks.
    series = series[(series.index-pd.Timedelta(days=6) >= frame.date.min()) & (series.index <= frame.date.max())]
    data = features(series)
    if len(data) < 40:
        return {'status': 'insufficient_data', 'required': 'At least 48 complete weeks', 'future': [], 'history': []}
    test_size = min(12, len(data)//4)
    train, test = data.iloc[:-test_size], data.iloc[-test_size:]
    xcols = data.columns.drop('y')
    model = XGBRegressor(n_estimators=120,max_depth=3,learning_rate=.04,subsample=.9,random_state=42,n_jobs=1)
    model.fit(train[xcols],train.y)
    # Evaluate the same recursive multi-week task used in serving: no held-out actual lags.
    train_series = series[series.index < test.index.min()]
    def predict_recursive(history, count, use_model):
        history = history.copy()
        predictions = []
        for _ in range(count):
            date = history.index[-1]+pd.Timedelta(days=7)
            baseline = float(history.iloc[-4:].mean())
            row = {f'lag_{lag}': history.iloc[-lag] for lag in [1,2,4,8]}
            row.update(rolling_4=baseline, month=date.month, week=date.isocalendar().week)
            value = max(0,float(model.predict(pd.DataFrame([row])[xcols])[0])) if use_model else baseline
            history.loc[date] = value
            predictions.append(value)
        return predictions
    baseline = predict_recursive(train_series,test_size,False)
    predicted = predict_recursive(train_series,test_size,True)
    baseline_metrics, model_metrics = metrics(test.y,baseline), metrics(test.y,predicted)
    chosen = model_metrics['mae'] < baseline_metrics['mae']*.98
    model.fit(data[xcols],data.y)
    future = predict_recursive(series,horizon,chosen)
    return {'status': 'ok', 'selected_model': 'XGBoost' if chosen else '4-week moving average',
            'baseline_metrics': baseline_metrics, 'xgboost_metrics': model_metrics,
            'evaluation': 'Chronological recursive holdout; XGBoost requires at least 2% lower MAE.',
            'history': [{'date': str(d.date()), 'actual': float(v)} for d,v in series.items()],
            'holdout': [{'date': str(d.date()),'actual': float(a),'baseline': float(b),'xgboost': float(p)} for d,a,b,p in zip(test.index,test.y,baseline,predicted)],
            'future': [{'date': str((series.index[-1]+pd.Timedelta(weeks=i+1)).date()),'predicted': v} for i,v in enumerate(future)],
            'caveat': 'Weekly units; recursive forecasts. No calibrated uncertainty interval. Filter to a product/category for its demand.'}
