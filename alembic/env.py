import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# Загружаем переменные окружения из .env
from dotenv import load_dotenv
load_dotenv()

# Импорт базы данных и моделей
from models import Base  # если вы создали models.py как выше


# Alembic конфигурация
config = context.config

# Задаём URL к БД из .env
db_url = os.getenv("DATABASE_URL")

if not db_url:
    raise ValueError("❌ Переменная окружения DB_URL не найдена!")

config.set_main_option("sqlalchemy.url", db_url)

# Логирование
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Мета-данные моделей (нужны для autogenerate)
target_metadata = Base.metadata

def run_migrations_offline():
    """Запуск миграций в оффлайн-режиме (без подключения к БД)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Запуск миграций в онлайн-режиме (с подключением к БД)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

# Определяем режим запуска
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
