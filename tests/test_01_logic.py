from src.services.lootbox import LootboxEngine
from src.core.config import settings

def run_tests():
    print("=== ЗАПУСК ВЕРИФИКАЦИИ МАТЕМАТИЧЕСКОГО ЯДРА СИНДИКАТА ===")
    engine = LootboxEngine()
    
    # 1. Тестируем симуляцию одного открытия
    print("\n[Тест 1] Проверка атомарного открытия:")
    res = engine.simulate_single_opening(box_type="normal", is_vip=True)
    print(f"-> Запущен {res['box_name']} для {res['user_tier']}")
    print(f"-> Достигнут шаг: {res['step_reached']} (Взрыв: {res['is_exploded']}) | Награда: {res['reward_al']} AL")
    assert res["success"] is True, "Ошибка симуляции"

    # 2. Искусственно создаем историю открытий игрока для проверки агрегации
    # Допустим, за стрим юзер открыл два бокса:
    # Попытка А (Тир-1, дошел до 3 шага): Обычная награда за 3 шаг = 220 AL
    # Попытка Б (Тир-2, дошел до 5 шага): Обычная награда за 5 шаг = 605 AL
    mock_history = [
        {"box_name": "Тир-1 (50 БК)", "user_tier": "normal", "step_reached": 3, "reward_al": 220},
        {"box_name": "Тир-2 (250 БК)", "user_tier": "normal", "step_reached": 5, "reward_al": 605}
    ]
    
    print("\n[Тест 2] Проверка систем агрегации валюты:")
    
    # Проверяем режим TOTAL_ACCUMULATIVE (Сумма всех боксов)
    settings.REWARD_SYSTEM_MODE = "TOTAL_ACCUMULATIVE"
    total_res = engine.aggregate_stream_rewards(mock_history)
    print(f"-> Режим TOTAL_ACCUMULATIVE: {total_res} AL (Ожидается: 220 + 605 = 825)")
    assert total_res == 825, "Ошибка TOTAL_ACCUMULATIVE"
    
    # Проверяем режим ABSOLUTE_MAX (Только лучший бокс)
    settings.REWARD_SYSTEM_MODE = "ABSOLUTE_MAX"
    max_res = engine.aggregate_stream_rewards(mock_history)
    print(f"-> Режим ABSOLUTE_MAX: {max_res} AL (Ожидается: max(220, 605) = 605)")
    assert max_res == 605, "Ошибка ABSOLUTE_MAX"
    
    # Проверяем режим STEP_ACCUMULATIVE (Сумма шагов внутри лучшей коробки)
    # Попытка А (Тир-1): Шаг 1(100) + Шаг 2(150) + Шаг 3(220) = 470 AL
    # Попытка Б (Тир-2): Шаг 1(110) + Шаг 2(165) + Шаг 3(242) + Шаг 4(385) + Шаг 5(605) = 1507 AL
    settings.REWARD_SYSTEM_MODE = "STEP_ACCUMULATIVE"
    step_res = engine.aggregate_stream_rewards(mock_history)
    print(f"-> Режим STEP_ACCUMULATIVE: {step_res} AL (Ожидается: max(470, 1507) = 1507)")
    assert step_res == 1507, "Ошибка STEP_ACCUMULATIVE"

    print("\n✅ ВСЕ ТЕСТЫ СИСТЕМЫ УСПЕШНО ПРОЙДЕНЫ! АРХИТЕКТУРА СТАБИЛЬНА.")

if __name__ == "__main__":
    run_tests()
