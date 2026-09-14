# Контекст и архитектура проекта «Танковый Синдикат»

## Текущий Спринт: Разработка асинхронной инфраструктуры БД (TS-2)
**Статус:** В разработке (In Progress)
**Текущая ветка:** `feature/TS-2-database-models`

## Структура файлов проекта (Текущее состояние)
├── .gitignore              # Исключения Git
├── STANDARDS.md            # Набор корпоративных стандартов разработки
├── CONTEXT.md              # Данный файл (Слепок контекста)
├── main.py                 # Единственная точка входа в корне проекта
├── .env                    # [Локальный] Переменные окружения (секреты, URL базы)
├── tests/                  # Папка для всех тестов и симуляций
│   ├── test_logic.py       # Тесты математического ядра лутбоксов
│   └── test_db.py          # [Будет создан] Тесты инициализации и связей БД
└── src/                    # Основной пакет исходного кода приложения
    ├── __init__.py         
    ├── core/               
    │   ├── __init__.py     
    │   ├── config.py       # Конфигурация проекта (Pydantic-Settings, RewardMode)
    │   └── db.py           # [Будет создан] Асинхронный движок и фабрика сессий БД
    ├── models/             
    │   ├── __init__.py     
    │   └── database.py     # [Будет создан] Декларативные модели таблиц SQLAlchemy 2.0
    └── services/           
        ├── __init__.py     
        └── lootbox.py      # Математическое ядро лутбоксов (LootboxEngine)

## Спецификация существующих модулей

### 1. Модуль: src/core/config.py
*   **Класс:** `Settings(BaseSettings)` — Синглтон конфигурации `settings`.
*   **Динамические поля:** `GLOBAL_BASE_REWARD` (int), `VIP_LOOT_MULTIPLIER` (float), `REWARD_SYSTEM_MODE` (Literal["ABSOLUTE_MAX", "TOTAL_ACCUMULATIVE", "STEP_ACCUMULATIVE"]), `DATABASE_URL` (str), `VK_VIDEO_API_URL` (str).
*   **Константные матрицы:** `TIER_CONFIG` (бонусы к луту и шансам тиров), `BASE_CHANCES` (базовые шансы шагов 1-6), `STEP_MULTIPLIERS` (прогрессия наград шагов 1-6).

### 2. Модуль: src/services/lootbox.py
*   **Класс:** `LootboxEngine`
    *   `simulate_single_opening(box_type: str, is_vip: bool) -> dict`: Симуляция 6 шагов до первого взрыва. Возвращает сырой результат: `step_reached`, `is_exploded`, `reward_al`.
    *   `aggregate_stream_rewards(box_results: list) -> int`: Агрегирует историю логов открытий за весь стрим и рассчитывает итоговый баланс AL по выбранному `REWARD_SYSTEM_MODE`.
    *   `_calculate_box_reward(loot_mult, step_reached, is_vip) -> int`: Внутренний формульный расчет награды.
