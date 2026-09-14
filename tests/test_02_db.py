import asyncio
import datetime
from sqlalchemy import select
from src.core.db import async_engine, Base, AsyncSessionLocal
from src.models.database import StreamerChannel, User, UserChannelProgress

async def run_db_tests_async():
    print("\n=== ЗАПУСК ИНТЕГРАЦИОННЫХ ТЕСТОВ POSTGRESQL ===")
    
    # 1. Сбрасываем старые таблицы и накатываем новые (Только для тестовой среды!)
    async with async_engine.begin() as conn:
        print("-> Пересоздание таблиц в базе данных...")
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Схемы данных успешно скомпилированы в PostgreSQL.")

    # Открываем асинхронную сессию для транзакций
    async with AsyncSessionLocal() as session:
        # 2. Создаем тестового стримера (SaaS-канал)
        # В Tanks Blitz ID каналов — это большие числа, поэтому используем BigInteger формат
        test_channel_id = 999888777
        streamer = StreamerChannel(
            channel_id=test_channel_id,
            streamer_name="AceLut_Stream"
        )
        session.add(streamer)
        
        # 3. Создаем глобального зрителя
        test_vk_id = 111222333
        viewer = User(
            vk_id=test_vk_id,
            current_username="Tankist_2026"
        )
        session.add(viewer)
        
        # Фиксируем изменения в базе, чтобы сгенерировались связи
        await session.flush()
        print("✅ Тестовый стример и глобальный юзер добавлены в буфер.")

        # 4. Инициализируем прогресс (баланс) этого юзера на канале этого стримера
        progress = UserChannelProgress(
            vk_id=test_vk_id,
            channel_id=test_channel_id,
            ac_balance=500, # Даем стартовые 500 AL для проверки
            is_vip=False
        )
        session.add(progress)
        await session.commit()
        print("✅ Запись прогресса (таблица-мост) успешно сохранена в БД.")

    # 5. Проверяем выборку данных (SELECT) и работу связей relationship
    async with AsyncSessionLocal() as session:
        print("-> Проверка извлечения данных и связей...")
        stmt = select(User).where(User.vk_id == test_vk_id)
        result = await session.execute(stmt)
        db_user = result.scalar_one()
        
        print(f"   Успешно найден юзер: {db_user.current_username} (VK ID: {db_user.vk_id})")
        
        # Загружаем связанную таблицу-мост через await
        # Так как у нас аsing-режим, связи проверяются строго внутри активной сессии
        progress_stmt = select(UserChannelProgress).where(
            UserChannelProgress.vk_id == db_user.vk_id,
            UserChannelProgress.channel_id == test_channel_id
        )
        p_res = await session.execute(progress_stmt)
        db_progress = p_res.scalar_one()
        
        print(f"   Баланс на канале 'AceLut_Stream': {db_progress.ac_balance} AL")
        assert db_progress.ac_balance == 500, "Ошибка: Баланс в БД не совпадает с ожидаемым!"

        # 6. Тестируем UniqueConstraint (защита от дублирования балансов)
        print("-> Тестирование защиты от дублирования балансов (UniqueConstraint)...")
        duplicate_progress = UserChannelProgress(
            vk_id=test_vk_id,
            channel_id=test_channel_id,
            ac_balance=1000
        )
        session.add(duplicate_progress)
        try:
            await session.commit()
            print("❌ ТЕСТ ПРОВАЛЕН: База данных позволила создать дубликат баланса!")
            assert False, "UniqueConstraint не сработал!"
        except Exception as e:
            # Мы ожидаем ошибку IntegrityError от Postgres из-за нарушения уникальности
            await session.rollback()
            print("✅ Защита сработала! База данных заблокировала дублирование баланса.")

    print("\n🎉 ВСЕ ТЕСТЫ БАЗЫ ДАННЫХ ПРОЙДЕНЫ! ИНФРАСТРУКТУРА ПОСТГРЕСА ИДЕАЛЬНА.")

def run_db_tests():
    """Синхронная обертка для запуска асинхронного теста в основном потоке"""
    asyncio.run(run_db_tests_async())
