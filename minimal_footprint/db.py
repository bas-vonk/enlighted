from sqlalchemy import Table, UniqueConstraint, create_engine
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Engine, RowMapping
from sqlalchemy.orm import Query


def get_engine(settings) -> Engine:
    """Get database engine."""
    return create_engine(
        f"postgresql+psycopg2://{settings.db_username}:{settings.db_password}"
        f"@{settings.db_hostname}:{settings.db_port}/{settings.db_database}",
        future=True,
    )


def create_all_tables(Base, engine: Engine) -> None:
    """Create all tables."""
    Base.metadata.create_all(engine)


def insert_into(table: Table, db: Engine, data: dict) -> None:
    with db.connect() as conn:
        conn.execute(insert(table).values(data))
        conn.commit()


def upsert(table, engine: Engine, data: dict) -> None:
    """Upsert in database."""

    # Find unique constraint
    unique_constraint = None
    for arg in table.__table_args__:
        if isinstance(arg, UniqueConstraint):
            unique_constraint = arg
            break

    if unique_constraint is None:
        raise Exception(f"No unique constraint defined for table {table.__tablename__}")

    with engine.connect() as conn:
        conn.execute(
            insert(table)
            .values(data)
            .on_conflict_do_update(unique_constraint, set_=data)
        )
        conn.commit()


def fetchone(engine: Engine, query: Query) -> RowMapping:
    with engine.connect() as conn:
        exec = conn.execute(query)
        result = exec.fetchone()
        return result._mapping if result is not None else None
