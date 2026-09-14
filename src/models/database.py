import datetime
from typing import List, Optional
from sqlalchemy import BigInteger, ForeignKey, UniqueConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.db import Base

class StreamerChannel(Base):
    """
    Таблица каналов стримеров (SaaS изоляция).
    Хранит уникальные ID каналов VK Видео Live и их настройки.
    """
    __tablename__ = "streamer_channels"

    channel_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    streamer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow, nullable=False)

    # Связи (Relationships) с каскадным удалением мусора
    sessions: Mapped[List["StreamSession"]] = relationship(
        back_populates="channel", cascade="all, delete-orphan"
    )
    progress_records: Mapped[List["UserChannelProgress"]] = relationship(
        back_populates="channel", cascade="all, delete-orphan"
    )
    box_logs: Mapped[List["LootboxLog"]] = relationship(
        back_populates="channel", cascade="all, delete-orphan"
    )


class StreamSession(Base):
    """Сессии трансляций для фиксации АФК-статусов, лимитов и расчета налогов."""
    __tablename__ = "stream_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    channel_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("streamer_channels.channel_id", ondelete="CASCADE"), nullable=False)
    is_live: Mapped[bool] = mapped_column(default=True, nullable=False)
    started_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow, nullable=False)
    ended_at: Mapped[Optional[datetime.datetime]] = mapped_column(default=None, nullable=True)

    channel: Mapped["StreamerChannel"] = relationship(back_populates="sessions")
    box_logs: Mapped[List["LootboxLog"]] = relationship(back_populates="session", cascade="all, delete-orphan")


class User(Base):
    """Глобальная таблица зрителей VK Видео. ID привязан жестко к цифровому VK ID."""
    __tablename__ = "users"

    vk_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    current_username: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Резерв под интеграцию с Lesta API
    lesta_account_id: Mapped[Optional[int]] = mapped_column(BigInteger, unique=True, nullable=True)
    lesta_nickname: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    channel_progress: Mapped[List["UserChannelProgress"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    box_logs: Mapped[List["LootboxLog"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class UserChannelProgress(Base):
    """Таблица-мост: Балансы и винстрики зрителя на КОНКРЕТНОМ канале стримера."""
    __tablename__ = "user_channel_progress"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    vk_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.vk_id", ondelete="CASCADE"), nullable=False)
    channel_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("streamer_channels.channel_id", ondelete="CASCADE"), nullable=False)
    
    ac_balance: Mapped[int] = mapped_column(default=0, nullable=False)
    is_vip: Mapped[bool] = mapped_column(default=False, nullable=False)
    visit_streak: Mapped[int] = mapped_column(default=0, nullable=False)
    last_stream_id: Mapped[int] = mapped_column(default=0, nullable=False)
    last_active_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow, nullable=False)

    user: Mapped["User"] = relationship(back_populates="channel_progress")
    channel: Mapped["StreamerChannel"] = relationship(back_populates="progress_records")

    # Жесткое бизнес-правило: один юзер — одна запись прогресса на одном канале
    __table_args__ = (UniqueConstraint("vk_id", "channel_id", name="_vk_channel_uc"),)


class LootboxLog(Base):
    """История логов открытий для аналитики, красивых выводов и проверки АФК."""
    __tablename__ = "lootbox_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    vk_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.vk_id", ondelete="CASCADE"), nullable=False)
    channel_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("streamer_channels.channel_id", ondelete="CASCADE"), nullable=False)
    session_id: Mapped[int] = mapped_column(ForeignKey("stream_sessions.id", ondelete="CASCADE"), nullable=False)
    
    box_type: Mapped[str] = mapped_column(String(20), nullable=False) # cheap, normal, elite
    step_reached: Mapped[int] = mapped_column(nullable=False) # 1-6
    is_exploded: Mapped[bool] = mapped_column(nullable=False)
    reward_al: Mapped[int] = mapped_column(nullable=False)
    opened_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow, nullable=False)

    user: Mapped["User"] = relationship(back_populates="box_logs")
    channel: Mapped["StreamerChannel"] = relationship(back_populates="box_logs")
    session: Mapped["StreamSession"] = relationship(back_populates="box_logs")
