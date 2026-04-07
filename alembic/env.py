"""
Alembic env.py for asynchronous operations with PostgreSQL.
This file manages all database migration operations.
"""

from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from alembic import context
import asyncio
from pathlib import Path
import sys

# Add application to PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import config and models
from app.config import get_settings
from app.models import Base

# This is the Config object that interprets the Alembic config file
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set metadata for autogenerate migrations
target_metadata = Base.metadata

# Get DATABASE_URL from config
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database_url)


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    
    This configures the context with a database URL and calls the metadata,
    but does not create an Engine.
    
    Useful for developing migrations and their generation.
    """
    configuration = config.get_section(config.config_ini_section)
    if configuration is None:
        configuration = {}
    configuration["sqlalchemy.url"] = settings.database_url

    context.configure(
        url=configuration.get("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Runs migrations in an asynchronous context."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    Run migrations in asynchronous mode.
    
    Creates an asynchronous engine and runs migrations.
    """
    configuration = config.get_section(config.config_ini_section)
    if configuration is None:
        configuration = {}

    configuration["sqlalchemy.url"] = settings.database_url

    connectable: AsyncEngine = create_async_engine(
        settings.database_url,
        poolclass=pool.NullPool,
    )

    async with connectable.begin() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations() -> None:
    """
    Run migrations depending on context.
    
    If offline - uses offline mode,
    otherwise runs asynchronous migrations.
    """
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        asyncio.run(run_async_migrations())


run_migrations()
