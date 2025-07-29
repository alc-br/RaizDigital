# alembic/env.py - CÓDIGO FINALMENTE CORRIGIDO

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Importe a Base dos seus modelos para que o autogenerate funcione
from app.models import Base
# Importe a função que carrega as configurações do seu projeto
from app.config import get_settings

# esta é a configuração do Alembic, que fornece
# acesso aos valores do arquivo .ini em uso.
config = context.config

# Interprete o arquivo de configuração para o logging do Python.
# Esta linha basicamente configura os loggers.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Carregue as configurações da sua aplicação para obter a URL do banco
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database_url)

# adicione o objeto MetaData do seu modelo aqui
# para suporte ao 'autogenerate'
target_metadata = Base.metadata

# outras opções, como nome do schema, etc., podem ser definidas aqui
# para autogenerate support
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def run_migrations_offline() -> None:
    """Roda as migrações no modo 'offline'."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Roda as migrações no modo 'online'."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())