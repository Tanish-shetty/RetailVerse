import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .core.config import settings
from .api.routes import router

app = FastAPI(title='RetailIQ',version='1.0.0',description='Evidence-based FMCG analytics; synthetic development dataset.')
app.add_middleware(CORSMiddleware,allow_origins=settings().cors_origins.split(','),allow_methods=['GET','POST'],allow_headers=['Content-Type'])
app.include_router(router)


@app.get('/health')
def health():
    return {'status':'ok','data_source':settings().data_source}


@app.exception_handler(Exception)
async def unavailable(request: Request, exception: Exception):
    logging.getLogger(__name__).exception('Request failed',exc_info=exception)
    return JSONResponse(status_code=503,content={'detail':'Analytics unavailable. Check dataset ingestion and database configuration.'})
