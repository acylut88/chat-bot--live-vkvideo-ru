from pathlib import Path
from typing import Dict, Any, Literal
from pydantic_settings import BaseSettings, SettingsConfigDict

# Ограничиваем типы режимов начисления валюты на уровне типов Python
RewardMode = Literal["ABSOLUTE_MAX", "TOTAL_ACCUMULATIVE", "STEP_ACCUMULATIVE"]

class Settings(BaseSettings):
    """
    Глобальный класс конфигурации платформы 'Танковый Синдикат'.
    Автоматически подтягивает настройки из файла .env, если он существует.
    """
    
    # --- НАСТРОЙКИ СТРИМЕРА (Динамические, можно переопределить через .env) ---
    GLOBAL_BASE_REWARD: int = 100
    VIP_LOOT_MULTIPLIER: float = 1.5
    
    # Текущий режим начисления AL за стрим для геймификации
    REWARD_SYSTEM_MODE: RewardMode = "TOTAL_ACCUMULATIVE"
    
    # --- СЕТЕВЫЕ НАСТРОЙКИ (Потребуются для будущих спринтов) ---
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/tank_syndicate"
    VK_VIDEO_API_URL: str = "https://vkvideo.ru"
    
    # --- ЖЕСТКИЕ ИГРОВЫЕ МАТРИЦЫ (Константы экономики, DRY-подход) ---
    # Множители наград и бонусы к шансам для каждого ТИРа
    TIER_CONFIG: Dict[str, Dict[str, Any]] = {
        "cheap":  {"loot_mult": 1.00, "chance_bonus": 0.00, "label": "Тир-1 (50 БК)"},
        "normal": {"loot_mult": 1.10, "chance_bonus": 0.05, "label": "Тир-2 (250 БК)"},
        "elite":  {"loot_mult": 1.25, "chance_bonus": 0.10, "label": "Тир-3 (1000 БК)"}
    }

    # Базовые шансы прохождения шагов (Вариант 3: Мягкий фарм)
    BASE_CHANCES: Dict[int, float] = {
        1: 0.90, 2: 0.80, 3: 0.70, 4: 0.60, 5: 0.50, 6: 0.30
    }

    # Линейные множители шагов внутри одной цепочки
    STEP_MULTIPLIERS: Dict[int, float] = {
        1: 1.0, 2: 1.5, 3: 2.2, 4: 3.5, 5: 5.5, 6: 10.0
    }

    # Настройка Pydantic для чтения файла .env из корня проекта
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore" # Игнорировать лишние переменные в .env
    )

# Инициализируем синглтон конфигурации для импорта в другие модули
settings = Settings()
