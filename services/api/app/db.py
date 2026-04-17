from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlmodel import Session, create_engine

from .config import settings

engine = create_engine(settings.database_url, echo=False)


def get_alembic_config(database_url: str | None = None) -> Config:
    api_root = Path(__file__).resolve().parents[1]
    config = Config(str(api_root / 'alembic.ini'))
    config.set_main_option('script_location', str(api_root / 'alembic'))

    resolved_url = database_url or engine.url.render_as_string(hide_password=False)
    config.set_main_option('sqlalchemy.url', resolved_url)
    return config


def run_migrations(database_url: str | None = None) -> None:
    command.upgrade(get_alembic_config(database_url), 'head')


def get_session():
    with Session(engine) as session:
        yield session
