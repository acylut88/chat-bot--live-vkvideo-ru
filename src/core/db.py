from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from src.core.config import settings
from typing import AsyncGenerator

# 1. Создаем асинхронный движок (Engine) подключения к PostgreSQL.
# Он отвечает за пул соединений (connection pool) и сетевой обмен с СУБД.
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # Выставь True, если хочешь видеть сырые SQL-запросы в консоли при отладке
    pool_pre_ping=True,  # Защита: проверяет живой ли коннект перед каждым запросом
)

# 2. Создаем фабрику сессий (Sessionmaker). 
# Каждая сессия — это изолированная транзакция в базу данных.
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Защищает объекты от инвалидации после коммита (стандарт для асинхронности)
)

# 3. Базовый декларативный класс для всех моделей.
# Все наши таблицы в src/models/database.py будут наследоваться от него.
class Base(DeclarativeBase):
    pass

# Вспомогательная функция-генератор сессий (потребуется для FastAPI зависимостей / Dependency Injection)
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Обеспечивает контролируемое открытие и закрытие сессии БД."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()