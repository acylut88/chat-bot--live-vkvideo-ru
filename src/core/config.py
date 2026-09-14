from pathlib import Path
from typing import Dict, Any, Literal
from pydantic_settings import BaseSettings, SettingsConfigDict

RewardMode = Literal["ABSOLUTE_MAX", "TOTAL_ACCUMULATIVE", "STEP_ACCUMULATIVE"]

class Settings(BaseSettings):
    """
    Глобальная конфигурация платформы.
    Динамически собирает URL подключения к PostgreSQL из переменных окружения.
    """
    # --- НАСТРОЙКИ ПОДКЛЮЧЕНИЯ К ПОСТГРЕСУ ---
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "tank_syndicate"

    # --- ИГРОВЫЕ НАСТРОЙКИ СТРИМЕРА ---
    GLOBAL_BASE_REWARD: int = 100
    VIP_LOOT_MULTIPLIER: float = 1.5
    REWARD_SYSTEM_MODE: RewardMode = "TOTAL_ACCUMULATIVE"
    
    VK_VIDEO_API_URL: str = "https://vkvideo.ru"
    
    # Использование свойства (property) позволяет получить готовую строку подключения на лету
    @property
    def DATABASE_URL(self) -> str:
        """Собирает DSN строку с использованием асинхронного драйвера asyncpg."""
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # --- ИГРОВЫЕ КОНСТАНТЫ (МАТРИЦЫ) ---
    TIER_CONFIG: Dict[str, Dict[str, Any]] = {
        "cheap":  {"loot_mult": 1.00, "chance_bonus": 0.00, "label": "Тир-1 (50 БК)"},
        "normal": {"loot_mult": 1.10, "chance_bonus": 0.05, "label": "Тир-2 (250 БК)"},
        "elite":  {"loot_mult": 1.25, "chance_bonus": 0.10, "label": "Тир-3 (1000 БК)"}
    }
    BASE_CHANCES: Dict[int, float] = {
        1: 0.90, 2: 0.80, 3: 0.70, 4: 0.60, 5: 0.50, 6: 0.30
    }
    STEP_MULTIPLIERS: Dict[int, float] = {
        1: 1.0, 2: 1.5, 3: 2.2, 4: 3.5, 5: 5.5, 6: 10.0
    }

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
