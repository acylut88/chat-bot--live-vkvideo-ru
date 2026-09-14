# Контекст и архитектура проекта «Танковый Синдикат»

## Текущий Спринт: Рефакторинг структуры под стандарт Clean Architecture (TS-1.5)
**Статус:** В разработке

## Структура файлов проекта
├── .gitignore              # Исключения Git
├── STANDARDS.md            # Набор корпоративных стандартов разработки
├── CONTEXT.md              # Данный файл (Слепок контекста)
├── main.py                 # ЕДИНСТВЕННАЯ точка входа в корне проекта
├── tests/                  # Папка для всех тестов и симуляций
│   └── test_logic.py       
└── src/                    # Основной пакет приложения
    ├── __init__.py         
    ├── core/               
    │   ├── __init__.py     
    │   └── config.py       # Изолированная конфигурация
    └── services/           
        ├── __init__.py     
        └── lootbox.py      # Переименованный logic.py (Математическое ядро)


## Спецификация модулей, классов и данных

### 1. Модуль: config.py
*   **Класс/Структура:** `LootboxTierConfig`, `LootboxChancesConfig`
*   **Назначение:** Хранение множителей наград, базовых шансов, лимитов открытий.

### 2. Модуль: logic.py
*   **Класс:** `LootboxEngine`
    *   `__init__(self, config)`: Принимает конфигурацию.
    *   `calculate_drop(box_type: str, is_vip: bool, current_opens: int) -> dict`: Расчет цепочки из 6 шагов.
        *   *Вход:* `box_type` (str: cheap/normal/elite), `is_vip` (bool), `current_opens` (int).
        *   *Выход:* `dict` (`success`, `box_name`, `user_tier`, `step_reached`, `is_exploded`, `reward_al`, `error`).
    *   `_calculate_reward_amount(...)`: Внутренний метод подсчета AL по формуле "Мягкого фарма".

### Модуль: src/core/config.py
*   **Класс:** `Settings(BaseSettings)`
*   **Поля:** `REWARD_SYSTEM_MODE` (str), `GLOBAL_BASE_REWARD` (int), сетевые доступы.

### Модуль: src/services/lootbox.py
*   **Класс:** `LootboxEngine`
*   *Метод:* `simulate_chain(box_type: str, is_vip: bool) -> dict` — чистая симуляция 6 шагов одного бокса.
*   *Метод:* `process_stream_rewards(box_logs: list, mode: str) -> int` — расчет итогового баланса AL на основе выбранного стримером режима.
