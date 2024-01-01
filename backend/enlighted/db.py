# type: ignore

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session


class DbConfig(BaseSettings):
    db_username: str
    db_password: str
    db_hostname: str
    db_database: str
    db_schema: str
    db_port: str


class AuthDbConfig(DbConfig):
    model_config = SettingsConfigDict(env_prefix="auth_")


class BronzeDbConfig(DbConfig):
    model_config = SettingsConfigDict(env_prefix="bronze_")


class SilverDbConfig(DbConfig):
    model_config = SettingsConfigDict(env_prefix="silver_")


class GoldDbConfig(DbConfig):
    model_config = SettingsConfigDict(env_prefix="gold_")


def get_engine(config) -> Engine:
    return create_engine(
        f"postgresql+psycopg2://{config.db_username}:{config.db_password}"
        f"@{config.db_hostname}:{config.db_port}/{config.db_database}",
        execution_options={"schema_translate_map": {None: config.db_schema}},
        future=True,
        pool_pre_ping=True,
        pool_recycle=60,
    )


def get_session(config_per_table) -> Session:
    session = Session()

    for table, config in config_per_table.items():
        session.bind_table(table, get_engine(config))

    return session
