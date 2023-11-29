from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def get_engine(
    username: str, password: str, hostname: str, database: str, port: str
) -> Engine:
    """Get database engine."""
    return create_engine(
        f"postgresql+psycopg2://{username}:{password}" f"@{hostname}:{port}/{database}",
        future=True,
        pool_pre_ping=True,
        pool_recycle=60,
    )
