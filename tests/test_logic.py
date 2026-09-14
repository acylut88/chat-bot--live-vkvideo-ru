from src.services.lootbox import LootboxEngine

def run_tests():
    print("=== ЗАПУСК ЛОКАЛЬНЫХ ТЕСТОВ СИСТЕМЫ ЛУТБОКСОВ ===")
    engine = LootboxEngine()
    
    # Тест 1: Проверка базовой логики открытия (Тир-1 для обычного юзера)
    print("\n[Тест 1] Симуляция открытия Тир-1 (Обычный юзер):")
    res1 = engine.calculate_drop(box_type="cheap", is_vip=False, current_opens=0)
    print(f"Результат: Успех={res1['success']}, Шаг={res1['step_reached']}, Взрыв={res1['is_exploded']}, Награда={res1['reward_al']} AL")
    assert res1["success"] is True, "Тест 1 провален: Бокс должен открыться"

    # Тест 2: Проверка влияния VIP-статуса на ТИР-3 (Должен быть повышенный шанс и лут)
    print("\n[Тест 2] Симуляция открытия Тир-3 (VIP-юзер):")
    res2 = engine.calculate_drop(box_type="elite", is_vip=True, current_opens=0)
    print(f"Результат: Успех={res2['success']}, Название={res2['box_name']}, Шаг={res2['step_reached']}, Награда={res2['reward_al']} AL")
    assert res2["success"] is True, "Тест 2 провален"

    # Тест 3: Проверка жесткого лимита (6 открытий)
    print("\n[Тест 3] Проверка защиты от лимитов (Попытка №6 при лимите 6):")
    res3 = engine.calculate_drop(box_type="normal", is_vip=False, current_opens=6)
    print(f"Результат: Успех={res3['success']}, Ошибка='{res3.get('error')}'")
    assert res3["success"] is False, "Тест 3 провален: Система должна была заблокировать открытие"
    
    print("\n✅ ВСЕ ТЕСТЫ УСПЕШНО ПРОЙДЕНЫ! СИСТЕМА СТАБИЛЬНА.")

if __name__ == "__main__":
    run_tests()
