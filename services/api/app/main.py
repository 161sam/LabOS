from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db import run_migrations
from .services import mqtt_bridge as mqtt_bridge_service
from .services import scheduler as scheduler_service
from .routers import abrain, alerts, approvals, assets, auth, calibration, charges, dashboard, inventory, labels, maintenance, photos, reactor_control, reactor_health, reactor_ops, reactors, rules, safety, schedules, sensors, tasks, traces, users, vision, wiki
from .seed import seed_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    run_migrations()
    seed_data()
    mqtt_bridge_service.get_mqtt_bridge().start()
    scheduler_service.get_scheduler_runner().start()
    yield
    scheduler_service.get_scheduler_runner().stop()
    mqtt_bridge_service.get_mqtt_bridge().stop()


app = FastAPI(title=settings.app_name, version='0.1.0', lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=sorted({settings.public_web_base_url.rstrip('/'), 'http://localhost:3000', 'http://127.0.0.1:3000'}),
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
app.include_router(auth.router, prefix=api_prefix)
app.include_router(dashboard.router, prefix=api_prefix)
app.include_router(charges.router, prefix=api_prefix)
app.include_router(reactors.router, prefix=api_prefix)
app.include_router(reactor_ops.router, prefix=api_prefix)
app.include_router(reactor_control.router, prefix=api_prefix)
app.include_router(reactor_health.router, prefix=api_prefix)
app.include_router(assets.router, prefix=api_prefix)
app.include_router(inventory.router, prefix=api_prefix)
app.include_router(labels.router, prefix=api_prefix)
app.include_router(sensors.router, prefix=api_prefix)
app.include_router(photos.router, prefix=api_prefix)
app.include_router(vision.router, prefix=api_prefix)
app.include_router(rules.router, prefix=api_prefix)
app.include_router(tasks.router, prefix=api_prefix)
app.include_router(alerts.router, prefix=api_prefix)
app.include_router(calibration.router, prefix=api_prefix)
app.include_router(maintenance.router, prefix=api_prefix)
app.include_router(safety.router, prefix=api_prefix)
app.include_router(schedules.router, prefix=api_prefix)
app.include_router(users.router, prefix=api_prefix)
app.include_router(wiki.router, prefix=api_prefix)
app.include_router(abrain.router, prefix=api_prefix)
app.include_router(approvals.router, prefix=api_prefix)
app.include_router(traces.router, prefix=api_prefix)
