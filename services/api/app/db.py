from sqlalchemy import inspect, text
from sqlmodel import Session, SQLModel, create_engine
from .config import settings

engine = create_engine(settings.database_url, echo=False)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)
    _ensure_bootstrap_columns()


def _ensure_bootstrap_columns() -> None:
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())

    if 'reactor' not in table_names:
        return

    column_names = {column['name'] for column in inspector.get_columns('reactor')}
    statements: list[str] = []

    if 'last_cleaned_at' not in column_names:
        statements.append('ALTER TABLE reactor ADD COLUMN last_cleaned_at TIMESTAMP')
    if 'notes' not in column_names:
        statements.append('ALTER TABLE reactor ADD COLUMN notes VARCHAR')

    if not statements:
        return

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


def get_session():
    with Session(engine) as session:
        yield session
