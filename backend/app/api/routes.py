from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from ..db.repository import read_sales
from ..schemas.query import Filters, CopilotQuery, AnalyticsResponse, CopilotResponse
from ..services.analytics import analyze
from ..services.copilot import query

router = APIRouter(prefix='/api')


def filters(start: str | None = None, end: str | None = None, region: str | None = None,
            state: str | None = None, city: str | None = None, category: str | None = None,
            brand: str | None = None, product_id: str | None = None, promotion_id: str | None = None) -> Filters:
    from pydantic import ValidationError
    try:
        return Filters(**locals())
    except ValidationError:
        raise HTTPException(422,'Invalid filter values or date range')


FilterDep = Annotated[Filters, Depends(filters)]


@router.get('/filters')
def options():
    frame = read_sales()
    return {'options': {c: sorted(frame[c].unique().tolist()) for c in ['region','state','city','category','brand','product_id','promotion_id']},
            'start': str(frame.date.min().date()) if len(frame) else None,
            'end': str(frame.date.max().date()) if len(frame) else None,
            'source': frame.source.unique().tolist()}


def endpoint(operation):
    def get_data(filters: FilterDep, limit: int = Query(100,ge=1,le=1000), offset: int = Query(0,ge=0)):
        frame = read_sales(filters.model_dump())
        data = analyze(frame,operation)
        total = len(data) if isinstance(data,list) else None
        return {'data': data[offset:offset+limit] if isinstance(data,list) else data,
                'total':total, 'rows':len(frame),'source':frame.source.unique().tolist()}
    return get_data


for path, operation in {'/dashboard/overview':'overview','/sales/trend':'trend','/sales/by-region':'regions',
    '/sales/by-category':'categories','/products/top':'products','/products/performance':'products',
    '/customers/rfm':'rfm','/customers/segments':'segments','/promotions/performance':'promotions',
    '/forecast':'forecast','/anomalies':'anomalies'}.items():
    router.add_api_route(path,endpoint(operation),methods=['GET'],name=operation+'_'+path.split('/')[-1],response_model=AnalyticsResponse)


@router.post('/copilot/query',response_model=CopilotResponse)
def copilot(body: CopilotQuery):
    return query(body.question,body.filters.model_dump())
