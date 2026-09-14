import asyncio
import logging
from sqlalchemy import select
from src.core.db import async_engine, Base, AsyncSessionLocal
from src.models.database import StreamerChannel, StreamSession
from src.workers.chat import ChatWorker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SyndicateChatTest")

async def run_chat_worker_test_async():
    logger.info("=== ЗАПУСК БОЕВОГО MVP-ТЕСТА ЧАТ-ВОРКЕРА ===")
    
    # 1. Синхронизируем таблицы в PostgreSQL
    async with async_engine.begin() as conn:
        logger.info("-> Синхронизация таблиц БД...")
        await conn.run_sync(Base.metadata.create_all)
        
    # 2. ГАРАНТИРУЕМ НАЛИЧИЕ СТРИМЕРА И СЕССИИ В БД
    async with AsyncSessionLocal() as session:
        mock_channel_id = 888888
        
        # Проверяем и создаем стримера
        channel_stmt = select(StreamerChannel).where(StreamerChannel.channel_id == mock_channel_id)
        channel_res = await session.execute(channel_stmt)
        db_channel = channel_res.scalar_one_or_none()
        
        if not db_channel:
            logger.info(f"-> Инициализация тестового стримера {mock_channel_id} в PostgreSQL...")
            db_channel = StreamerChannel(channel_id=mock_channel_id, streamer_name="c1ymba_test")
            session.add(db_channel)
            await session.flush()
        
        # Проверяем и создаем сессию стрима под ID = 1
        session_stmt = select(StreamSession).where(StreamSession.id == 1)
        session_res = await session.execute(session_stmt)
        db_session = session_res.scalar_one_or_none()
        
        if not db_session:
            logger.info("-> Инициализация тестовой сессии стрима №1 в PostgreSQL...")
            db_session = StreamSession(id=1, channel_id=mock_channel_id, is_live=True)
            session.add(db_session)
            
        await session.commit()
        logger.info("✅ Вся тестовая инфраструктура СУБД готова к приему данных.")
        
    # 3. Инициализируем и запускаем наш Centrifugo воркер
    worker = ChatWorker()
    logger.info("🔥 Воркер запускается. Начинаем слушать живой чат стрима...")
    await worker.start()
    
    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        logger.info("🛑 Асинхронная задача остановлена.")

def run_chat_test():
    """Синхронная обертка для main.py"""
    try:
        asyncio.run(run_chat_worker_test_async())
    except KeyboardInterrupt:
        print("\nТест чата успешно завершен.")
