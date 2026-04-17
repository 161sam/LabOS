from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db import run_migrations
from .routers import abrain, alerts, assets, charges, dashboard, photos, reactors, rules, sensors, tasks, wiki
from .seed import seed_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    run_migrations()
    seed_data()
    yield


app = FastAPI(title=settings.app_name, version='0.1.0', lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/healthz')
def healthz():
    return {'status': 'ok'}


@app.get('/')
def root():
    return {'name': settings.app_name, 'version': '0.1.0'}


api_prefix = '/api/v1'
app.include_router(dashboard.router, prefix=api_prefix)
app.include_router(charges.router, prefix=api_prefix)
app.include_router(reactors.router, prefix=api_prefix)
app.include_router(assets.router, prefix=api_prefix)
app.include_router(sensors.router, prefix=api_prefix)
app.include_router(photos.router, prefix=api_prefix)
app.include_router(rules.router, prefix=api_prefix)
app.include_router(tasks.router, prefix=api_prefix)
app.include_router(alerts.router, prefix=api_prefix)
app.include_router(wiki.router, prefix=api_prefix)
app.include_router(abrain.router, prefix=api_prefix)
