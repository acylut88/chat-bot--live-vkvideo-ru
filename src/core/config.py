from dataclasses import dataclass, field
from typing import Dict

@dataclass(frozen=True)
class LootboxConfig:
    """
    Класс конфигурации лутбоксов.
    Используем frozen=True, чтобы сделать объект неизменяемым (Immutable).
    Это защищает настройки от случайного изменения в ходе выполнения программы.
    """
    GLOBAL_BASE_REWARD: int = 100
    MAX_OPENS_PER_STREAM: int = 6
    VIP_LOOT_MULTIPLIER: float = 1.5

    # Модификаторы тиров: (loot_mult, chance_bonus, красивое имя)
    TIER_MODIFIERS: Dict[str, Dict[str, any]] = field(default_factory=lambda: {
        "cheap":  {"loot_mult": 1.00, "chance_bonus": 0.00, "label": "Тир-1 (50 БК)"},
        "normal": {"loot_mult": 1.10, "chance_bonus": 0.05, "label": "Тир-2 (250 БК)"},
        "elite":  {"loot_mult": 1.25, "chance_bonus": 0.10, "label": "Тир-3 (1000 БК)"}
    })

    # Базовые шансы прохождения шагов (Вариант 3: Мягкий фарм)
    BASE_CHANCES: Dict[int, float] = field(default_factory=lambda: {
        1: 0.90,
        2: 0.80,
        3: 0.70,
        4: 0.60,
        5: 0.50,
        6: 0.30
    })

    # Множители наград за шаги
    STEP_MULTIPLIERS: Dict[int, float] = field(default_factory=lambda: {
        1: 1.0,
        2: 1.5,
        3: 2.2,
        4: 3.5,
        5: 5.5,
        6: 10.0
    })

# Создаем единый глобальный экземпляр настроек (паттерн Singleton / Shared Config)
settings = LootboxConfig()
