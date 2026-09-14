import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.database import User, UserChannelProgress

class UserDatabaseService:
    """Сервис для асинхронного управления состоянием пользователей и их балансов в БД."""
    
    @staticmethod
    async def process_chat_activity(
        session: AsyncSession, 
        vk_id: int, 
        username: str, 
        channel_id: int
    ) -> UserChannelProgress:
        """
        Регистрирует/обновляет пользователя и его локальный прогресс на канале.
        Блокирует строку прогресса для предотвращения Race Condition.
        """
        # 1. Проверяем глобального пользователя
        user_stmt = select(User).where(User.vk_id == vk_id)
        user_res = await session.execute(user_stmt)
        db_user = user_res.scalar_one_or_none()
        
        if not db_user:
            db_user = User(vk_id=vk_id, current_username=username)
            session.add(db_user)
            await session.flush()  # Генерируем ID без коммита транзакции
        else:
            if db_user.current_username != username:
                db_user.current_username = username

        # 2. Проверяем локальный прогресс на канале конкретного стримера
        # Использование свитча с блокировкой гарантирует стабильность баланса
        progress_stmt = (
            select(UserChannelProgress)
            .where(
                UserChannelProgress.vk_id == vk_id, 
                UserChannelProgress.channel_id == channel_id
            )
            .with_for_update()
        )
        progress_res = await session.execute(progress_stmt)
        db_progress = progress_res.scalar_one_or_none()
        
        if not db_progress:
            db_progress = UserChannelProgress(
                vk_id=vk_id, 
                channel_id=channel_id,
                ac_balance=0,
                is_vip=False
            )
            session.add(db_progress)
            
        # Обновляем штамп времени последней активности зрителя (в UTC)
        db_progress.last_active_at = datetime.datetime.utcnow()
        await session.flush()
        
        return db_progress
